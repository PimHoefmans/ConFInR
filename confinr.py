from datetime import datetime
import pandas as pd
import os
import click


DEFAULT_INIT_FOLDERS = ['INPUT', 'OUTPUT', 'ANNOTATION']


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
                    content += '>' + index + ' /1\n' + row['fw_seq'] + '\n' +\
                               '>' + index + ' /2\n' + row['rvc_seq'] + '\n'
                f.write(content)
        except KeyError:
            raise KeyError
        except ValueError:
            raise ValueError
    else:
        raise FileExistsError


@click.command()
@click.option('--input', help='Path to input file.')
@click.option('--output', help='Path for output file')
def preprocessing(i: str, o: str):
    """Call pre-processing function(s) to generate data for ConFInR.
    Call convert_to_fasta to extract sequences in TSV file and convert to FASTA file.
    :param i: Path to input file, type must be str.
    :param o: Path for output file, type must be str.
    """
    convert_to_fasta(load_input(i), o)


def initialize_run():
    t = datetime.now()
    run_id = ' '.join(['run', '-'.join([str(t.day), str(t.month), str(t.year)]),
                       '-'.join([str(t.hour), str(t.minute), str(t.second)])])
    try:
        if not os.path.exists(run_id):
            os.makedirs(run_id)
            os.chdir(run_id)
            for folder in DEFAULT_INIT_FOLDERS:
                os.makedirs(folder)
    except OSError:
        raise OSError


@click.command()
@click.option('--db', help='Path to DIAMOND database.')
@click.option('--i', help='Path to input file.')
@click.option('--makedb', help='Path to create DIAMOND database.')
def run(db, i, makedb):
    if(makedb):
        print('Make a DB')
        # function(makedb, db)
    # initialize_run()
    # function(db, i) > runs DIAMOND, stores output
    # function() > saves metadata
