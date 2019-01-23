from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, SelectField
from wtforms.validators import Optional

db_none_chosen = 'None'


class FastQForm(FlaskForm):
    forward_file = FileField(validators=[FileRequired()])
    reverse_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload', render_kw={'id': 'fastq_upload_button'})


class DiamondInputForm(FlaskForm):
    query_file = FileField('Query file',
                           validators=[FileRequired(),
                                       FileAllowed(['tsv', 'fasta', 'fastq', 'gz', 'zip'],
                                                   'Only tab-separated data or (compressed) FASTA/FASTQ')])
    db_file = FileField('Database file',
                        validators=[Optional(),
                                    FileAllowed(['fasta', 'gz', 'dmnd'],
                                                'Only pre-built DIAMOND database or (compressed) FASTA')])
    db_choice = SelectField('Existing database',
                            choices=[(db_none_chosen, 'None'), ('nr', 'NR database')],
                            default='None'
                            )
    submit = SubmitField('Upload')
