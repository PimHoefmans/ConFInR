import pandas as pd


# METAGEN-171
def load_input(file_path: str):
    """Load data from an input file in tab-separated format, convert to DataFrame and return only specific columns.
    :param file_path: Path to the input file, must be a string.
    :return: DataFrame with forward and reverse complement sequences.
    :raises KeyError: If requested key (e.g. sequence) is absent and can't be loaded.
    :raises FileNotFoundError: If file_path doesn't refer to an existing file.
    :raises ValueError: If an incorrect object type is used.
    """
    try:
        return pd.read_table(file_path, sep='\t', header='infer', index_col=0).loc[:, ['fw_seq', 'rvc_seq']]
    except KeyError:
        raise KeyError
    except FileNotFoundError:
        raise FileNotFoundError
    except ValueError:
        raise ValueError


# METAGEN-172
def create_fasta(df):
    return True
