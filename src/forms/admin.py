from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class addVehiclesForm(FlaskForm):
    type = StringField("Type", validators=[DataRequired(), Length(min=2)])
    submit = SubmitField("Add Vehicle")


class SigninForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=7)])
    submit = SubmitField("Signin")
