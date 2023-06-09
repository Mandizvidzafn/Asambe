from flask_wtf import FlaskForm
from wtforms import (
    TelField,
    PasswordField,
    SubmitField,
    SelectField,
    FileField,
    StringField,
)
from wtforms.validators import InputRequired, Length


class SigninForm(FlaskForm):
    phone = TelField("phone", validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired()])
    submit = SubmitField("Sign in")
