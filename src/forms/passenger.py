from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    TelField,
    SubmitField,
    BooleanField,
    IntegerField,
    FileField,
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
        ],
    )
    newsletter = BooleanField(
        "I want to recieve marketing information and updates",
        default=False,
    )

    submit = SubmitField("Sign up")


class SigninForm(FlaskForm):
    phone = StringField("Phone", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=7)])
    remember_me = BooleanField("remember me", default=True)
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    phone = TelField("Phone", validators=[InputRequired()])
    submit = SubmitField("Get OTP")


class VerifyOTPForm(FlaskForm):
    otp = StringField("Enter OTP", validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify")


class UpdateForm(FlaskForm):
    firstname = StringField("First Name", validators=[Length(min=2, max=40)])
    lastname = StringField("Last Name", validators=[Length(min=2, max=40)])
    phone = TelField("Phone")
    password = PasswordField("Password")
    confirm_password = PasswordField(
        "Confirm Password",
    )

    profile_image = FileField(
        "Change profile pic",
        validators=[
            FileAllowed(
                ["jpg", "png", "jpeg"],
                "Invalid file format. Only JPEG and PNG images are allowed!",
            )
        ],
    )

    submit = SubmitField("Update information")
