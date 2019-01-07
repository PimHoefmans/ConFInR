from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


class FastQForm(FlaskForm):
    forward_file = FileField(validators=[FileRequired()])
    reverse_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')


class DiamondInputForm(FlaskForm):
    query_file = FileField('Query file',
                           validators=[FileRequired(),
                                       FileAllowed(['tsv', 'fasta', 'fastq', 'gz'],
                                                   'Only tab-separated data or (compressed) FASTA/FASTQ')])
    db_file = FileField('Database file',
                        validators=[FileAllowed(['fasta', 'gz', 'dmnd'],
                                                'Only pre-built DIAMOND database or (compressed) FASTA')])
    submit = SubmitField('Upload')
