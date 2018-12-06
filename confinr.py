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
def preprocessing(i: str, o: str):
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
    """
    t = datetime.now()
    run_id = ' '.join(['RUN', '-'.join([str(t.day), str(t.month), str(t.year)]),
                       ''.join([str(t.hour)+'h', str(t.minute)+'m', str(t.second)+'s'])])
    try:
        if not os.path.exists(run_id):
            os.makedirs(run_id)
            os.chdir(run_id)
            for folder in DEFAULT_INIT_FOLDERS:
                os.makedirs(folder)
        return run_id
    except OSError:
        raise OSError


def write_metadata(i=None, db=None):
    """

    :param i:
    :param db:
    :return:
    """
    print(os.path.realpath(i))
    try:
        with open(METADATA_FILE_PATH, 'a+') as f:
            if i:
                f.write('Input file: '+i+'\n')
            if db:
                f.write('DIAMOND database ' + db + '\n')
    except OSError:
        raise OSError


def make_diamond_db(file, name, run_folder):
    """

    :param file:
    :param name:
    :param run_folder:
    :return:
    """
    os.chdir('../REFERENCE')
    arg = 'diamond makedb -in '+file+' -d '+name
    # TODO: Activate call(arg, shell=True)
    os.chdir('../'+run_folder)


def run_diamond(db, query, output='matches.m8'):
    """

    :param db:
    :param query:
    :param output:
    :return:
    """
    print(db)
    # TODO: Go to folder for reference
    print(query)
    print(output)
    command = 'diamond blastx -d <database> -q <input> -o <output>'
    return None


@click.command()
@click.option('--db', help='')
@click.option('--i', help='')
@click.option('--o', help='')
@click.option('--makedb', nargs=2, type=click.Tuple([str, str]), help='')
def run(db, i, o, makedb):
    # run_id = initialize_run()
    i_path = os.path.realpath(i)
    #
    # write_metadata(i=i_path)
    # if makedb:
    #     make_diamond_db(file=makedb[0], name=makedb[1], run_folder=run_id)
    #     db = makedb[1]

    run_diamond(db=db, query=i_path, output='mynamejeff.m8')

    # TODO: Call function to run DIAMOND.
    # TODO: Call function to store run metadata.
    return None

