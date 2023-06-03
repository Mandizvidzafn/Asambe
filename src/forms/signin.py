from flask_wtf import FlaskForm
from wtforms import TelField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired


class SigninForm(FlaskForm):
    phone = TelField("phone", validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired()])
    submit = SubmitField("Sign in")
