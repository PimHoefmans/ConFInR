from datetime import datetime
import pandas as pd
import os
import click


# METAGEN-171
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


# METAGEN-172
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


# METAGEN-167
def preprocessing():
    return ''


# FOLDER INITIALIZATION
def initialize():
    return ''
