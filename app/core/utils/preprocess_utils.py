import re
from Bio.Seq import Seq
from app.core.exceptions.exceptions import NonDNAException


# ALLOWED_EXTENSIONS = set(['fastq', 'csv', 'tsv'])
ALLOWED_EXTENSIONS = set(['fasta', 'fastq', 'tsv', 'csv', 'dmnd', 'gz'])


def get_reverse_complement(input_seq):
    """Return the reverse complement of a sequence.
    :param input_seq: DNA or RNA sequence, must be a string.
    :return: Reverse complement of input_seq.
    :raises NonDNAException: If the sequence contains non-DNA characters.
    :raises TypeError: If input_seq is not a string.
    """
    try:
        if check_dna(input_seq.upper()):
            return str(Seq(input_seq).reverse_complement())
        else:
            raise NonDNAException
    except TypeError:
        raise TypeError


def check_dna(seq, code=re.compile(r'[^ATCGN.]').search):
    """Check if a sequence consists of DNA-characters.
    :param seq: Sequence, must be a string
    :param code: Regex pattern
    :return: True or False
    """
    return not bool(code(seq))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
