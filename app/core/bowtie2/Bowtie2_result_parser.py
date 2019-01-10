import os
import pandas as pd
import dask as dd



def bowtie2_output_parser(fastq_df):
    """
    function to parse the sam file, that bowtie2 gives as output, and get the overlap locations and add the identity to the dataframe
    :param fastq_df: session dataframe
    :return:
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
            if accepted == True:
                identity = round(calculate_identity(fw_seq, rv_seq, fw_pair_pos, rv_pair_pos),2)
                headers.append(fw_header)
                identities.append(identity)

    df_columns = ["overlap_identity_perc"]
    df = pd.DataFrame(data=identities, columns=df_columns, index=headers)
    fastq_df = fastq_df.join(df)

    return fastq_df


def calculate_identity(fwseq, rvseq, fwpos, rvpos):
    """
    function tot calculate the identitie of the overlap of both sequences
    :param fwseq: forward sequence of a paired end read
    :param rvseq: reverse sequence of a paired end read
    :param fwpos: starting position of overlap on forward sequence
    :param rvpos: end position of overlap on reverse sequence
    :return:
    """
    rvseq = rvseq[0:rvpos -1]
    fwseq = fwseq[fwpos -1:len(fwseq)-1]
    overlap_len = len(rvseq)
    hit = 0
    for x in range(0,overlap_len):
        if fwseq[x] == rvseq[x]:
            hit += 1
    identity = 100 / overlap_len * hit
    return identity




