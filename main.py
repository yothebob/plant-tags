from flask import Flask, render_template, request
from forms import CreateEvalForm, CreateTagForm, RankEval
app = Flask(__name__)

tag_list = []
eval_list = []
related_list = []

def next_id(list_var):
    return len(list_var)
    
def updated_tag_rank(tags):
    for idx in tags:
        print(idx, get_tag_by_id(idx).name)
        tag = get_tag_by_id(idx)
        tag.rank = tag.rank + 1

def updated_related_tag_rank(obj_tags):
    for itm in obj_tags:
        itm.rank = itm.rank + 1


def get_tag_by_id(_id):
    for tt in tag_list:
        if tt.id == _id:
            return tt
        
def create_related_tag(taga, tagb):
    # for speed and consistancy tag1, tag2 is ordered by ID
    if taga == tagb:
        return
    tag1 = taga if taga.id < tagb.id else tagb
    tag2 = tagb if taga.id < tagb.id else taga
    
    found = False
    for item in related_list:
        if tag1 in item.related_tags:
            if tag2 in item.related_tags:
                found = True
                updated_related_tag_rank([tag1, tag2])
    if not found:
        if tag2.parent != tag1:
            new_related = RelatedTag([tag1, tag2])
            related_list.append(new_related)
    
        
class Eval():

    def __init__(self, tags=[], name="", result=0):
        self.id = next_id(eval_list)
        self.tags = tags
        self.name = name
        self.result = result

    def overall_rank(self):
        # TODO this needs to be a recursive function
        exact = self.find_full_eval_matches()
        # normally, get the next most unique. But we will cut the first one off.
        # because we already got exact matches
        next_tags = self.cut_most_unique_tag(self.tags)
        next_matches = self.find_evals_from_tags(next_tags)
        # After this try to chop next unique, if the next one is Essential. Then try to chop any that are not essential.
        # IF ALL of them are essential, then branch outwards by most related (from the most unique essential tag)
        round_three_tags = self.cut_most_unique_tag(next_tags)
        if round_three_tags == next_matches:
            # all essential so find closest related
            next_related = self.find_next_related()
            if next_related == None:
                # nothing new, return what we have
                return exact + next_matches
            else:
                round_three_tags = round_three_tags.append(next_related.id)
                round_three_matches = self.find_evals_from_tags(round_three_tags)
                return exact + next_matches + round_three_matches
        else:
            #drill down more, we cut off another tag with round 3. now find matches
            round_three_matches = self.find_evals_from_tags(round_three_tags)
        return exact + next_matches + round_three_matches
                
        
        
    def find_full_eval_matches(self):
        # a function for finding all matching evals with from self.tags (FULL MATCH)
        res = []
        for e in eval_list:
            full_match = True
            if self.id == e.id:
                continue
            for i in range(len(self.tags)):
                if self.tags[i-1] != e.tags[i-1]:
                    full_match = False
                    break
            if full_match:
                res.append(e)
        return res

    
    def find_evals_from_tags(self, tags_to_match=None):
        # a function for finding all matching evals with given tag_list
        res = []
        for e in eval_list:
            full_match = True
            if self.id == e.id:
                continue
            e.tags.sort()
            for et in e.tags:
                if et not in tags_to_match:
                    print("broke here", et)
                    full_match = False
                    break
            if full_match:
                res.append(e)
        return res

    
    def find_next_unique(self, tags, current_tag):
        # first find the most unique  note: tags is a list of Tag objects
        max_unique = 10000
        tag = None
        for t in tags:
            if t.id == current_tag.id:
                continue
            if t.rank < max_unique:
                tag = t
                max_unique = t.rank
        return tag


    def cut_most_unique_tag(self, tagid_list):
        # return a tagid_list that cuts off the most unique tag.
        # if ALL are essential, then return the same list
        most_unique = 100000
        most_unique_tag = 0
        updated = False
        for t in tagid_list:
            t_tag = get_tag_by_id(t)
            if t_tag.rank < most_unique and t_tag.essential == False:
                most_unique_tag = t
                most_unique = t_tag.rank
                updated = True
        if updated == False:
            return tagid_list
        return [tid for tid in tagid_list if tid != most_unique_tag]
    
    def find_next_related(self, current_tag):
        # find the next related tag from a given tag NOTE current_tag is Tag Object
        max_relation = 0
        new_tag = None
        for rt in related_list:
            # this has to also offer something new? so one id needs to be in the current tag BUT
            # the other id cannot be in the Eval Tag list
            id_matches = [tid for tid in rt.related_tags if tid in self.tags]
            print(len(id_matches))
            if len(id_matches) == 2:
                continue
            if current_tag.id in [t.id for t in rt.related_tags] and rt.rank > max_relation:
                max_relation = rt.rank
                new_tag = rt
        return new_tag
    
    
        
class Tag():

    def __init__(self, name="", parent=None, essential=False, rank=0):
        self.id = next_id(tag_list)
        self.name = name
        self.parent = parent
        self.essential = essential
        self.rank = rank


class RelatedTag():

    def __init__(self, related_tags=[], rank=0):
        self.id = next_id(tag_list)
        self.related_tags = [] # sort these by id, first is primary
        self.rank = rank
        
        
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add-tag", methods=["GET", "POST"])
def add_tag():
    form = CreateTagForm(request.form)
    if request.method == "POST":
        if form.parent.data != -10:
            print("add parent", tag_list[form.parent.data])
            optional_parent = tag_list[form.parent.data]
        else :
            optional_parent = None
            print(form.essential.data)
        new_tag = Tag(
            form.tag_name.data,
            optional_parent,
            form.essential.data
        )
        tag_list.append(new_tag)
        form.parent.choices = [(-10, "---")] + [((t), tag_list[(t)].name) for t in range(len(tag_list))]
        
        return render_template("add-tag.html", form=form, tags=tag_list)
    else:
        form.parent.choices = [(-10, "---")] + [((t), tag_list[(t)].name) for t in range(len(tag_list))]
        return render_template("add-tag.html", form=form, tags=tag_list)

    
@app.route("/add-eval", methods=["GET", "POST"])
def add_eval():
    form = CreateEvalForm(request.form)
    if request.method == "POST":
        new_eval = Eval(
            form.tags.data,
            form.name.data,
            form.result.data,
        )
        print(form.tags.data)
        updated_tag_rank(form.tags.data)
        eval_list.append(new_eval)
        for i in tag_list:
            for ii in tag_list:
                create_related_tag(i, ii)
                
        form.tags.choices = [(t.id, t.name) for t in tag_list]
        return render_template("add-eval.html", form=form, tags=tag_list)
    else:
        form.tags.choices = [(t.id, t.name) for t in tag_list]
        return render_template("add-eval.html", form=form, evals=tag_list)


@app.route("/rank", methods=["GET", "POST"])
def rank_eval():
    rankings = []
    form = RankEval(request.form)
    form.Eval.choices = [(e.id, e.name) for e in eval_list]
    if request.method == "POST":
        # print(form.Eval.data)
        found_eval = [e for e in eval_list if e.id == form.Eval.data][0]
        rankings = found_eval.overall_rank()
        return render_template("rank.html", form=form, rankings=rankings)
    else:
        return render_template("rank.html", form=form, rankings=rankings)

    
if __name__ == "__main__":
    app.run()
