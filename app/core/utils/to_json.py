import pandas as pd
import collections
import json
import math


def seq_length_to_json(df):
    """Convert sequence length distribution to JSON object.
    :param df: DataFrame containing a subset of sequence length.
    :return: JSON object for visualization of sequence length distribution.
    """
    json_data = {}
    for column in list(df):
        json_values = []
        distribution = collections.Counter(df.loc[:, column].dropna().tolist())
        for key, value in distribution.items():
            json_values.append({"x": int(key), "y": value})
        json_data[column] = json_values
    return json.dumps(json_data)


def perc_count_to_json(df):
    df_count = pd.Series.to_frame(df)
    df_count.index.names = ["perc"]
    return df_count.to_json(orient="table")


def get_paired_percentage_to_json(df):
    json_paired_data = []
    paired_seqs = df.groupby(["paired"]).size()
    if paired_seqs.count() < 2:
        json_paired_data.append({"name": "True", "y": 100})
        json_paired_data.append({"name": "False", "y": 0})
        return json.dumps(json_paired_data)
    else:
        paired_seq_number = paired_seqs.get_values()
        true_values = paired_seq_number[1]
        false_values = paired_seq_number[0]
        total = true_values + false_values
        true_values_percentage = round((true_values/total)*100, 3)
        false_values_percentage = round((false_values/total)*100, 3)
        json_paired_data.append({"name": "True", "y": true_values_percentage})
        json_paired_data.append({"name": "False", "y": false_values_percentage})
        return json.dumps(json_paired_data)


def nucleotide_percentages_to_json(df, bin_size, prefix):
    """Bin and convert nucleotide percentages to JSON object.
    Binning percentages reduces variety to a smaller number of groups, e.g. 0-50% and 50-100%.
    :param df: DataFrame containing a subset of nucleotide percentages.
    :param bin_size: Size of bin in percentage points.
    :param prefix: Prefix stating the strand, either "fw_" or "rv_", must be a string.
    :return: JSON object for visualization of nucleotide percentages.
    """
    postfix = "_perc"

    df = df.applymap(lambda x: math.ceil(x / bin_size) * bin_size)
    df = df.apply(pd.Series.value_counts).reset_index()
    json_data = []

    nucleotide_columns = df.drop("index", axis=1).columns
    for index_row, row in enumerate(df['index']):
        for index_col, col in enumerate(nucleotide_columns):
            if pd.notnull(df[col][index_row]):
                y = int(max(row-(bin_size/2), 0))
                y_min_bs = int(max(y-(bin_size/2), 0))
                y_plus_bs = int(min(y+(bin_size/2), 100))
                json_data.append(
                    {"label": str(col.replace(prefix, "").replace(postfix, "")),
                     "x": int(index_col), "y": y, "z": int(df[col][index_row]), "bin": str(y_min_bs)+"-"+str(y_plus_bs)}
                )
    return json_data
