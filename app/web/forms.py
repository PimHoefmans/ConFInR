from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import IntegerField, SubmitField, SelectField, RadioField
from config import Config


class FastQForm(FlaskForm):
    forward_file = FileField(validators=[FileRequired()])
    reverse_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')


class TSVForm(FlaskForm):
    tsv_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')

class DiamondForm(FlaskForm):
    matrix = [('BLOSUM45','BLOSUM45'),('BLOSUM50','BLOSUM50'), ('BLOSUM62','BLOSUM62'), ('BLOSUM80','BLOSUM80'),('BLOSUM90','BLOSUM90'), ('PAM250','PAM250'), ('PAM70','PAM70'), ('PAM30','PAM30')]
    outfmt = [('0','BLAST pairwise format'),('5','BLAST XML format'), ('6','BLAST tabular format'), ('100','Diamond Alignment Archive (DAA) format'), ('101','SAM format'), ('102','Taxonomic classification'), ('103','PAF format')]

    sensitivity = RadioField('Sensitivity', choices = [('','No extra sensitivity'),('sensitive ','Sensitive'),('more-sensitive ','More sensitive')])    
    frameshift = IntegerField("Frameshift", "Please enter the penalty for a frameshift")
    gapopen = IntegerField("Gap Open Penalty", "Please enter the penalty when opening a gap")
    gapextend = IntegerField("Gap Extend Penalty", "Please enter the penalty when extending a gap")
    matrix = SelectField("Matrix", choices = matrix)
    algorithm =  SelectField('Algorithm', choices = [('0','Double Indexed'),('1','Query Indexed')])
    outfmt = SelectField('Format of the output file', choices = outfmt)
    compress = SelectField('Compression', choices = [('0','No compression'), ('1','Gzip compression') ])
    max_target_seqs = IntegerField('Maximum number of target sequences', 'Please enter the maximum number of target sequences per query')
    e_value = IntegerField('E-Value','Please enter the maximum e-value')
    min_score = IntegerField('Minimum bit score','Please enter the minimum bit score')
    identity = IntegerField('Identity Percentage','Please enter the minimum percentage of sequence identity')
    query_cover = IntegerField('Query coverage','Please enter the minimum percentage of query coverage')
    subject_cover = IntegerField('Subject coverage','Please enter the minimum percentage of subject coverage')
    max_hsps = IntegerField('Maximum number of HSPs','Please enter the maximum number of HSPs per subject sequence')
    submit = SubmitField("Run Diamond")
