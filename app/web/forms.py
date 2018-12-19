from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class FastQForm(FlaskForm):
    forward_file = FileField(validators=[FileRequired()])
    reverse_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')


class TSVForm(FlaskForm):
    tsv_file = FileField('Input file:',
                         validators=[FileRequired(), FileAllowed(['tsv', 'txt', 'fasta', 'gz'], 'Tab-separated data only!')])
    plebus = SubmitField('Upload')


class DatabaseForm(FlaskForm):
    db_file = FileField('Input file:',
                        validators=[FileRequired(), FileAllowed(['fasta', 'gz'], '(Compressed) FASTA only!')])
    name = StringField('Database name:', validators=[DataRequired()])
    spqr = SubmitField('Upload')


class DiamondForm(FlaskForm):
    input_file = FileField(validators=[FileRequired()])
    # INSERT OTHER FIELDS
    submit = SubmitField('Upload')