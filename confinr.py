from subprocess import call
from datetime import datetime
import pandas as pd
import os
import click

DEFAULT_INIT_FOLDERS = ['OUTPUT', 'ANNOTATION']
METADATA_FILE_PATH = 'metadata.txt'


def load_input(input_path: str):
    """Load data from tab-separated input file, convert to DataFrame and return only columns with sequences.
    :param input_path: Path to the input file, type must be str.
    :return: DataFrame with forward and reverse complement sequences.
    :raises KeyError: If requested key (e.g. sequence) is absent and can't be loaded.
    :raises FileNotFoundError: If file_path doesn't refer to an existing file.
    :raises ValueError: If an incorrect object type is used.
    """
    try:
        return pd.read_table(input_path, sep='\t', header='infer', index_col=0).loc[:, ['fw_seq', 'rvc_seq']]
    except KeyError:
        raise KeyError
    except FileNotFoundError:
        raise FileNotFoundError
    except ValueError:
        raise ValueError


def convert_to_fasta(df: pd.DataFrame, output_path: str):
    """Convert sequences and headers in DataFrame to FASTA-format.
    Include postfixes '/1' for forward- and '/2' for reverse complement sequences in FASTA header.
    :param df: DataFrame containing sequences (columns) and headers (row indices), type must be pd.DataFrame.
    :param output_path: Path to output file, type must be str.
    :return: File with sequences in FASTA-format.
    :raises KeyError: If requested key (e.g. sequence) is absent and can't be loaded.
    :raises ValueError: If an incorrect object type is used.
    :raises FileExistsError: If output_path refers to an existing file.
    """
    if not os.path.exists(output_path):
        try:
            content = ''
            with open(output_path, 'w') as f:
                for index, row in df.iterrows():
                    if isinstance(row['fw_seq'], str):
                        content += '>' + index + ' /1\n' + row['fw_seq'] + '\n'
                    if isinstance(row['rvc_seq'], str):
                        content += '>' + index + ' /2\n' + row['rvc_seq'] + '\n'
                f.write(content)
        except KeyError:
            raise KeyError
        except ValueError:
            raise ValueError
    else:
        raise FileExistsError


@click.command()
@click.option('--i', help='Path to input file.')
@click.option('--o', help='Path for output file')
def preprocess(i: str, o: str):
    """Call pre-processing function(s) to generate data for ConFInR.
    Call convert_to_fasta to extract sequences in TSV file and convert to FASTA file.
    :param i: Path to input file, type must be str.
    :param o: Path for output file, type must be str.
    """
    convert_to_fasta(load_input(i), o)


def initialize_run():
    """Initialize a ConFInR run by creating the required folder structure.
    Run folder name contains the date and time of the run.
    :raises OSError: If there is no such file or directory.
    :return: Run folder name.
    """
    t = datetime.now()
    run_id = ' '.join(['RUN', '-'.join([str(t.day), str(t.month), str(t.year)]),
                       ''.join([str(t.hour) + 'h', str(t.minute) + 'm', str(t.second) + 's'])])
    try:
        if not os.path.exists(run_id):
            os.makedirs(run_id)
            os.chdir(run_id)
            for folder in DEFAULT_INIT_FOLDERS:
                os.makedirs(folder)
        return run_id
    except OSError:
        raise OSError


def write_metadata(q=None, d=None):
    # TODO: Write documentation
    try:
        with open(METADATA_FILE_PATH, 'a+') as f:
            if q:
                f.write('Query file: ' + q + '\n')
            if d:
                f.write('DIAMOND database ' + d + '\n')
    # TODO: Add BLAST mode
    # TODO: Add optional parameters
    except OSError:
        raise OSError


@click.command()
@click.argument('ref', envvar='REFERENCE')
@click.option('--i', help='Path to the input protein reference database file.')
@click.option('--d', help='Path to the output DIAMOND database file.')
def make_diamond_db(i: str, d: str):
    """Run a shell command that creates a DIAMOND database.
    :param ref: REFERENCE directory path to store database in.
    :param i: Input file to create database with, either file name or full path to the file, type must be str.
    :param d: Database name, type must be str.
    """
    # TODO: Implement ref as environment variable to ensure generic writing to correct folder.
    command = 'diamond makedb --in ' + i + ' -d ' + d
    call(command, shell=True)


def run_diamond(d: str, q: str, run_id: str):
    """Create path for o (output file) based on default folder structure.
    Create path for d (database file) based on default folder structure if d is not an existing path.
    Run a shell command that executes DIAMOND in BLASTX mode.
    :param d: Path to the DIAMOND database file, type must be str.
    :param q: Path to the query input file, type must be str.
    :param run_id: Run folder name, type must be str.
    """
    o = os.getcwd() + '\OUTPUT\matches.m8'
    if not os.path.exists(d):
        os.chdir('..')
        d = os.getcwd() + '\REFERENCE\\' + d
        os.chdir(run_id)
    command = 'diamond blastx -d ' + d + ' -q ' + q + ' -o ' + o
    call(command, shell=True)


@click.command()
@click.option('--d', help='Path to the DIAMOND database file.')
@click.option('--q', help='Path to the query input file.')
def run_confinr(d, q):
    # TODO: Write documentation.
    run_id = initialize_run()
    write_metadata(q=os.path.realpath(q))
    run_diamond(d, q, run_id)
    # TODO: Correctly handle d file path write_metadata(d=os.path.realpath(d))
    # TODO: Add option to generically pass further arguments.
