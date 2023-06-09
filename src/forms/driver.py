from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileAllowed
from wtforms import (
    BooleanField,
    StringField,
    RadioField,
    PasswordField,
    TelField,
    SubmitField,
    FileField,
)


class SignupForm(FlaskForm):
    firstname = StringField(
        "First Name", validators=[InputRequired(), Length(min=2, max=40)]
    )
    lastname = StringField(
        "Last Name", validators=[InputRequired(), Length(min=2, max=40)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=2, max=40)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            Length(min=2, max=40),
        ],
    )
    phone = TelField("Phone", validators=[InputRequired()])
    vehicle_choices = [
        ("bus", "bus"),
        ("quantum", "quantam"),
        ("quza", "quza"),
        ("van", "van"),
    ]
    vehicle = RadioField(
        "Type of vehicle", choices=vehicle_choices, validators=[InputRequired()]
    )
    newsletter = BooleanField(
        "I want to reacieve marketing information and updates", default=False
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


class UpdateForm(FlaskForm):
    firstname = StringField("First Name", validators=[Length(min=2, max=40)])
    lastname = StringField("Last Name", validators=[Length(min=2, max=40)])
    phone = TelField("Phone")
    password = PasswordField("Password")
    confirm_password = PasswordField("Confirm Password")

    vehicle_choices = [
        ("bus", "bus"),
        ("quantum", "quantum"),
        ("quza", "quza"),
        ("van", "van"),
    ]
    # vehicle = RadioField("Type of vehicle", choices=vehicle_choices)

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
