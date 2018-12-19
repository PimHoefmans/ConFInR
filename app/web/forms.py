from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class FastQForm(FlaskForm):
    forward_file = FileField(validators=[FileRequired()])
    reverse_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')


class DiamondInputForm(FlaskForm):
    tsv_file = FileField('Query file:',
                         validators=[FileRequired(), FileAllowed(['tsv', 'txt', 'fasta', 'gz'], 'Tab-separated data only!')])
    # TODO: Text explaining format(s)
    db_file = FileField('Database file:',
                        validators=[FileRequired(), FileAllowed(['fasta', 'gz'], '(Compressed) FASTA only!')])
    # TODO: Text explaining format(s)
    submit = SubmitField('Upload')