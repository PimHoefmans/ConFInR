import click
import pandas as pd


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


def convert_to_fasta(df: pd.DataFrame, output_path: str):
    """Convert tab-delimited data (.TSV) to FASTA format and write to a file.

    Include postfixes '/1' (forward sequences) and '/2' (reverse complement sequences) in FASTA header.
    Write formatted data to a file.
    :param df: DataFrame, should contain columns 'fw_seq' and 'rvc_seq' & headers as row indices to extract data from.
    :param output_path: Path to output file.
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
@click.argument('i')
@click.option('--o', default='output.fasta', help='Path for output file')
def convert(i: str, o: str):
    """Convert tab-delimited data (in .TSV file) to FASTA format (in .FASTA file).

    :param i: Path to input file.
    :param o: Optional path for output file.
    """
    convert_to_fasta(load_input(i), o)
