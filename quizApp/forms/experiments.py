from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, HiddenField, \
        RadioField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString, Input

class DateTimeWidget(object):
    def __call__(self, field, **kwargs):
        output = ('<div class="input-group date" id="{}">'
                  '<input type="text" class="form-control {}"'
                  '    name="{}", value="{}"/>'
                  '<span class="input-group-addon">'
                  '    <span class="glyphicon'
                  '    glyphicon-calendar"></span>'
                  '    </span>'
                  '</div>'
                  '<script type="text/javascript">'
                  '    $(function () {{'
                  '        $("#{}").datetimepicker({{'
                  '             format: "YYYY-MM-DD HH:mm:ss"'
                  '         }});'
                  '    }});'
                  '</script>').format(field.id,
                                      kwargs.pop("class_", ""),
                                      field.name,
                                      kwargs.pop("value", ""),
                                      field.id)
        return HTMLString(output)

class TextAreaWidget(Input):
    input_type = "text"
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('value', field._value())

        return HTMLString("<textarea %s></textarea>" % \
                          self.html_params(name=field.name, **kwargs))

class LikertWidget(object):
    def __call__(self, field, **kwargs):
        # Likert widget from Pete Fectau's example
        output = "<ul class='likert'>\n"
        for choice in field.choices:
            output += ('<li>\n'
                       '  <input type="radio" name="{}" value="{}">\n'
                       '  <label>{}</label>\n'
                       '</li>\n').format(field.name, choice[0], choice[1])

        output += "</ul>\n"
        return HTMLString(output)

class CreateExperimentForm(Form):
    name = StringField("Name", validators=[DataRequired()])
    start = DateTimeField("Start time", widget=DateTimeWidget(),
                          validators=[DataRequired()])
    stop = DateTimeField("Stop time", widget=DateTimeWidget(),
                        validators=[DataRequired()])
    submit = SubmitField("Submit")

class DeleteExperimentForm(Form):
    exp_id = HiddenField()
    submit = SubmitField("Submit")

class QuestionForm(Form):
    submit = SubmitField("Submit")
    reflection = StringField(widget=TextAreaWidget())

class MultipleChoiceForm(QuestionForm):
    answers = RadioField(validators=[DataRequired()])

class ScaleForm(QuestionForm):
    answers = RadioField(validators=[DataRequired()], widget=LikertWidget())

class LoginForm(Form):
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password")
    submit = SubmitField("Login")