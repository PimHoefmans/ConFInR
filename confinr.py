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
        return pd.read_table(input_path, sep='\t', header='infer', index_col=0, comment='#').loc[:, ['fw_seq', 'rvc_seq']]
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


def write_metadata(q=None, d=None, run_id=None, p=None):
    """Write metadata file for ConFInR run to list input file, -database and parameters.
    :param q: Path to query file.
    :param d: Path to DIAMOND database.
    :param run_id: Run folder name.
    :param p: Optional DIAMOND parameters.
    :raises OSError: If there is no such file or directory.
    """
    try:
        with open(METADATA_FILE_PATH, 'a+') as f:
            if q is not None:
                f.write('Query file:\t' + q + '\n')
            if d is not None:
                if not os.path.exists(d):
                    os.chdir('..')
                    d = os.getcwd() + '/REFERENCE/' + d.split('/')[-1]
                    os.chdir(run_id)
                f.write('DIAMOND database:\t' + d + '\n')
            if p is not None:
                f.write('DIAMOND parameters: ' + ''.join(list('\t' + item.rstrip() + '\n' for item in p.replace('--',
                        ',--').split(',')[1:])) + '\n')
    # TODO: Add BLAST mode
    # TODO: Add optional parameters
    except OSError:
        raise OSError


@click.command()
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


def run_diamond(d: str, q: str, run_id: str, params=None):
    """Create path for o (output file) based on default folder structure.
    Create path for d (database file) based on default folder structure if d is not an existing path.
    Add optional DIAMOND parameters to shell command is parameter params is not None.
    Run a shell command that executes DIAMOND in BLASTX mode.
    :param d: Path to the DIAMOND database file, type must be str.
    :param q: Path to the query input file, type must be str.
    :param run_id: Run folder name, type must be str.
    :param params: Optional DIAMOND parameters, multiple parameters should be surrounded with quotes, type must be str.
    """
    o = './OUTPUT/matches.m8'
    if not os.path.exists(d):
        os.chdir('..')
        d = os.getcwd() + '/REFERENCE/' + d
        os.chdir(run_id)
    command = 'diamond blastx -d ' + d + ' -q ' + q + ' -o ' + o
    if params is not None:
        command += ' '+params
    call(command, shell=True)


@click.command()
@click.option('--d', help='Path to the DIAMOND database file.')
@click.option('--q', help='Path to the query input file.')
@click.option('--params', help='Optional DIAMOND parameters.')
def run_confinr(d: str, q: str, params=None):
    """Perform a ConFInR run: initialize run folder structure, run DIAMOND and write metadata file.
    :param d: Path to the DIAMOND database file, type must be str.
    :param q: Path to the query input file, type must be str.
    :param params: Optional DIAMOND parameters, multiple parameters should be surrounded with quotes, type must be str.
    """
    run_id = initialize_run()
    run_diamond(d, q, run_id, params)
    write_metadata(q=os.path.realpath(q))
    write_metadata(d=os.path.realpath(d), run_id=run_id)
    write_metadata(p=params)
    # TODO: EXCEPTION d and q must be passed
