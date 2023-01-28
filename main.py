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
        tag = tag_list[idx -1]
        tag.rank = tag.rank + 1

def updated_related_tag_rank(obj_tags):
    for itm in obj_tags:
        itm.rank = itm.rank + 1

def create_related_tag(tag1, tag2):
    print(related_list)
    found = False
    for item in related_list:
        if tag1 in item.related_tags:
            print("hit")
            if tag2 in item.related_tags:
                print("double hit")
                found = True
                updated_related_tag_rank([tag1, tag2])
    if not found:
        new_related = RelatedTag([tag1, tag2])
        related_list.append(new_related)
    
        
class Eval():

    def __init__(self, tags=[], name="", result=0):
        self.id = next_id(eval_list)
        self.tags = tags
        self.name = name
        self.result = result

    def find_exact_tags(self):
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

    def find_next_unique(tags, current_tag):
        """
        # first find the most unique
        max_unique = 100
        tag = None
        for t in tags:
            if t.id ==current_tag.id:
                continue
            if t.rank > max_unique:
                tag = t
                max_unique = t.rank
        return tag
        """        
        pass

    def find_next_related(current_tag):
        """
        max_relation = 0
        new_tag = None
        for rt in related_list:
            if current_tag.id in [t.id for t in rt.tags] && rt.rank > max_relation:
                max_reltion = rt.rank
                new_tag = rt
        return new_tag
        """        
        pass
    
    
        
class Tag():

    def __init__(self, name="", parent=None, essential=False, rank=100):
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
        if len(tag_list) >= (form.parent.data - 1) and (form.parent.data - 1) > 0:
            optional_parent = tag_list[(form.parent.data - 1)]
        else :
            optional_parent = None
        new_tag = Tag(
            form.tag_name.data,
            optional_parent,
            form.essential.data
        )
        tag_list.append(new_tag)
        form.parent.choices = [(-1, "---")] + [(t.id, t.name) for t in tag_list]
        
        return render_template("add-tag.html", form=form, tags=tag_list)
    else:
        form.parent.choices = [(-1, "---")] + [(t.id, t.name) for t in tag_list]
        return render_template("add-tag.html", form=form, tags=tag_list)

    
@app.route("/add-eval", methods=["GET", "POST"])
def add_eval():
    form = CreateEvalForm(request.form)
    if request.method == "POST":
        print(form.tags.data)
        new_eval = Eval(
            form.tags.data,
            form.name.data,
            form.result.data,
        )
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
        rankings = found_eval.find_exact_tags()
        return render_template("rank.html", form=form, rankings=rankings)
    else:
        return render_template("rank.html", form=form, rankings=rankings)

    
if __name__ == "__main__":
    app.run()
