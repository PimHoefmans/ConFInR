import pandas as pd
import os
import zipfile

SEQUENCE_COLUMNS = ['fw_seq', 'rvc_seq']


def load_input(input_path: str):
    """Load tab-delimited input data.

    Load tab-delimited data from input file and convert to DataFrame.
    Exclude columns where 'flagged' (column) is False. Extract sequences from selected columns.
    :param input_path: Path to input file.
    :return: DataFrame with forward- and reverse complement sequences.
    :raises KeyError: If requested key (e.g. sequence) is absent and can't be loaded.
    :raises FileNotFoundError: If file_path doesn't refer to an existing file.
    :raises ValueError: If an incorrect object type is used.
    """
    try:
        df = pd.read_table(input_path, sep='\t', header='infer', index_col=0, comment='#')
        return df[~df.flagged].loc[:, SEQUENCE_COLUMNS]
    except KeyError:
        raise KeyError
    except FileNotFoundError:
        raise FileNotFoundError
    except ValueError:
        raise ValueError


def merge_input(input_path: str):
    """Merge zipped tab-delimited input data files.

    Load tab-delimited data from input zip and concatenate into single DataFrame.
    :param input_path: Path to input file.
    :return: DataFrame with forward- and reverse complement sequences.
    :raises KeyError: If requested key (e.g. sequence) is absent and can't be loaded.
    :raises FileNotFoundError: If file_path doesn't refer to an existing file.
    :raises ValueError: If an incorrect object type is used.
    """
    print('DEBUG: input_path:', input_path)
    print('DEBUG: read_table file name:', '/'.join([os.getcwd(), input_path.replace('.zip', ''), 'file']))
    try:
        with zipfile.ZipFile(input_path, 'r') as z:
            merged_df = pd.concat( [ pd.read_table('/'.join([ os.getcwd(), input_path.replace('.zip', ''), file ]),
                                                   sep='\t',
                                                   header='infer',
                                                   index_col=0,
                                                   comment='#') for file in z.namelist() if file.endswith('.tsv') ] )
            return merged_df
    except KeyError:
        raise KeyError
    except FileNotFoundError:
        raise FileNotFoundError
    except ValueError:
        raise ValueError


def convert_to_fasta(df: pd.DataFrame, uuid: str):
    """Convert tab-delimited data (.TSV) to FASTA format and write to a file.

    Include postfixes '/1' (forward sequences) and '/2' (reverse complement sequences) in FASTA header.
    Write formatted data to a file.
    :param df: DataFrame, should contain columns 'fw_seq' and 'rvc_seq' & headers as row indices to extract data from.
    :param uuid: Unique ID that refers to session ID.
    :raises KeyError: If requested key (e.g. sequence) is absent and can't be loaded.
    :raises ValueError: If an incorrect object type is used.
    :raises FileExistsError: If output_path refers to an existing file.
    """
    output_file = 'data/' + uuid + '/diamond/query/' + 'query.fasta'
    if not os.path.exists(output_file):
        try:
            content = ''
            with open(output_file, 'w') as f:
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
