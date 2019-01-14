import os
import pandas as pd


def bowtie2_output_parser(fastq_df):
    """
    Parse the SAM file provided by Bowtie2 as output to get overlapping locations and add identity scores to DataFrame.
    :param fastq_df: DataFrame containing FASTQ data.
    :return: Updated fastq_df DataFrame.
    """
    outputfile = os.path.abspath("data/Bowtie2_data/output/output.sam")
    headers = []
    identities = []
    with open(outputfile) as f:
        for line in f:
            accepted = True
            fwline = line.split("\t")
            rvline = f.readline().split("\t")
            fw_header, rv_header = "@"+fwline[0].strip(), "@"+rvline[0].strip()
            fw_pair_pos, rv_pair_pos = int(fwline[7]), int(rvline[7])
            fw_seq, rv_seq = fwline[9], rvline[9]
            if fw_header != rv_header:
                accepted = False
            if fw_pair_pos == 0 or rv_pair_pos == 0:
                accepted = False
            rv_pair_pos = (len(fw_seq) - fw_pair_pos)
            if accepted:
                identity = round(calculate_identity(fw_seq, rv_seq, fw_pair_pos, rv_pair_pos), 2)
                headers.append(fw_header)
                identities.append(identity)

    df_columns = ["overlap_identity_perc"]
    df = pd.DataFrame(data=identities, columns=df_columns, index=headers)
    fastq_df = fastq_df.join(df)

    return fastq_df


def calculate_identity(fw_seq, rv_seq, fw_pos, rv_pos):
    """
    Calculate identity of overlap between both sequences.
    :param fw_seq: Forward sequence of a paired end read.
    :param rv_seq: Reverse sequence of a paired end read.
    :param fw_pos: Starting position of overlap on forward sequence.
    :param rv_pos: End position of overlap on reverse sequence.
    :return: Identity score.
    """
    rv_seq = rv_seq[0:rv_pos - 1]
    fw_seq = fw_seq[fw_pos - 1:len(fw_seq) - 1]
    overlap_len = len(rv_seq)
    hit = 0
    for x in range(0,overlap_len):
        if fw_seq[x] == rv_seq[x]:
            hit += 1
    identity = 100 / overlap_len * hit
    return identity
