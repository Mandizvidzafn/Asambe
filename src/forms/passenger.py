from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    TelField,
    SubmitField,
    BooleanField,
    IntegerField,
)
from wtforms.validators import (
    EqualTo,
    Length,
    InputRequired,
    DataRequired,
    NumberRange,
    Regexp,
)


class SignupForm(FlaskForm):
    firstname = StringField(
        "First Name", validators=[InputRequired(), Length(min=2, max=40)]
    )
    lastname = StringField(
        "Last Name", validators=[InputRequired(), Length(min=2, max=40)]
    )
    phone = TelField("Phone", validators=[InputRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=7)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(min=7),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    newsletter = BooleanField(
        "I want to recieve marketing information and updates",
        default=False,
    )

    submit = SubmitField("Sign up")


class SigninForm(FlaskForm):
    phone = TelField("Phone", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=7)])
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    phone = TelField("Phone", validators=[InputRequired()])
    submit = SubmitField("Get OTP")


class VerifyOTPForm(FlaskForm):
    otp = StringField("Enter OTP", validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify")
