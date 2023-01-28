from wtforms import Form, SelectField, SubmitField, validators, SelectMultipleField, StringField, BooleanField, IntegerField
from wtforms.widgets import PasswordInput

class CreateTagForm(Form):

    tag_name = StringField("Name:")
    parent = SelectField(u'Parent:', coerce=int)
    essential = BooleanField('Essential?')
    submit = SubmitField("Submit")
    
# this is an eval for plants, so lets do that 
class CreateEvalForm(Form):
    tags = SelectMultipleField(u'Tags:', coerce=int)
    name = StringField("Name:")
    result = IntegerField("Result:")
    submit = SubmitField("Submit")

class RankEval(Form):
    Eval = SelectField(u'Eval:', coerce=int)
    submit = SubmitField("Submit")
