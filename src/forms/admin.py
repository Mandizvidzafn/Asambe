from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class addVehiclesForm(FlaskForm):
    type = StringField("Type", validators=[DataRequired(), Length(min=2)])
