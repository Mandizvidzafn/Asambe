from flask_wtf import FlaskForm
from wtforms import TelField, TextAreaField, EmailField, StringField, SubmitField
from wtforms.validators import InputRequired, Email


class FeedbackForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    phone = TelField("Phone Number", validators=[InputRequired()])
    email = EmailField("Email", validators=[Email()])
    subject = StringField("Subject", validators=[InputRequired()])
    message = TextAreaField(
        "Message", validators=[InputRequired()], render_kw={"rows": "10", "cols": "45"}
    )
    submit = SubmitField("submit")
