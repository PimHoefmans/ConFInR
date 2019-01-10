import numpy as np
import pandas as pd


def get_paired_reads(df):
    """Check if the forward and reverse complement are both present.
    :param df: DataFrame which has the columns "fw_seq" and "rvc_seq".
    :return: DataFrame with the column "paired" which has True if both sequences are present.
    """
    df['paired'] = df[["fw_seq", "rv_seq"]].notna().all(axis=1)


def get_nucleotide_percentages(df, prefix):
    """Calculate the percentages of nucleotides in a sequence.
    :param df: the main df
    :param prefix: Prefix stating the strand, either 'fw_' or 'rvc_', must be a string.
    :return: *new_df* DataFrame with percentages of nucleotides as columns.
    :raises NonDNAException: If the sequence contains non-DNA characters.
    :raises AttributeError: If input_seq has no attribute 'upper' because it is not a string.
    :raises TypeError: If input_seq or prefix is not a string.
    :raises ZeroDivisionError: If input_seq is an empty string.
    """
    try:
        df[prefix + 'A_perc'] = df[prefix + 'seq'].apply(lambda row: round(row.upper().count('A') / len(row) * 100, 4) if pd.notnull(row) else np.nan)
        df[prefix + 'T_perc'] = df[prefix + 'seq'].apply(lambda row: round(row.upper().count('T') / len(row) * 100, 4) if pd.notnull(row) else np.nan)
        df[prefix + 'G_perc'] = df[prefix + 'seq'].apply(lambda row: round(row.upper().count('G') / len(row) * 100, 4) if pd.notnull(row) else np.nan)
        df[prefix + 'C_perc'] = df[prefix + 'seq'].apply(lambda row: round(row.upper().count('C') / len(row) * 100, 4) if pd.notnull(row) else np.nan)
    except TypeError:
        raise TypeError
    except KeyError:
        raise KeyError


def get_sequence_length(df):
    """
    Calculates length for all sequences and adds this to the column x_seq_length
    :param df: Dataframe to insert the values to.
    :return: DataFrame with the total length of sequences as columns.
    :raises: TypeError: raised if the sequences aren't strings
    :raises: KeyError: raised if the label does not exist in the dataframe
    """
    try:
        df['fw_seq_length'] = df['fw_seq'].apply(lambda fw_len: len(fw_len) if pd.notnull(fw_len) else np.nan)
        df['rv_seq_length'] = df['rv_seq'].apply(lambda rv_len: len(rv_len) if pd.notnull(rv_len) else np.nan)
    except TypeError:
        raise TypeError
    except KeyError:
        raise KeyError
