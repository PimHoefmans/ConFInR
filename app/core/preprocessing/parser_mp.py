"""
Multiprocessed parser for fastq files
"""

import multiprocessing as mp
import os
import re

import dask.dataframe as dd
import numpy as np
import pandas as pd

from app.core.utils.preprocess_utils import get_reverse_complement

# regex pattern for the nucleotide sequence
SEQUENCE_PATTERN = re.compile("^[ATGCNYPatgcnyp]+")
# regex pattern for the sequence header
HEADER_PATTERN = re.compile("^@.*HWI.+(:\d+){3,10}.+")
# regex pattern for the + sign between the sequence and quality score
PLUS_PATTERN = re.compile("^\+")


def preprocess_fastq_files_mp(fw_file, rv_file, uuid: str):
    """

    :param fw_file: forward fastq file
    :param rv_file: reverse fastq file
    :param uuid: unique identifier saved in the flask session
    :return:
    """
    fastq_df = initialize_dataframe(fw_file, rv_file)
    fastq_df = extend_dataframe(fastq_df)
    fastq_df.to_parquet('data/' + uuid + '/parquet/', engine="pyarrow")


def initialize_dataframe(fw_file, rv_file):
    """
    process the forward and reverse fastq files by making workers process chunks of the files.
    :param fw_file: forward fastq file
    :param rv_file: reverse fastq file
    :return: dask dataframe
    """
    pool_fw = mp.Pool(mp.cpu_count() // 2)
    pool_rv = mp.Pool(mp.cpu_count() // 2)
    jobs_fw = []
    jobs_rv = []

    for chunkStart, chunkSize in chunkify(fw_file):
        jobs_fw.append(pool_fw.apply_async(process_fastq_chunk, (fw_file, chunkStart, chunkSize, False,)))

    for chunkStart, chunkSize in chunkify(rv_file):
        jobs_rv.append(pool_rv.apply_async(process_fastq_chunk, (rv_file, chunkStart, chunkSize, True,)))

    fw_result = {"index": [], "seq": [], "comp": [], "qual": []}
    rv_result = {"index": [], "seq": [], "comp": [], "qual": []}

    for r in jobs_fw:
        if r.get():
            fw_result['index'] += r.get()[0]  # index / sequence header
            fw_result['seq'] += r.get()[1]  # sequence
            fw_result['qual'] += r.get()[2]  # quality score
            fw_result['comp'] += r.get()[3]  # complement sequence
    for r in jobs_rv:
        if r.get():
            rv_result['index'] += r.get()[0]  # index / sequence header
            rv_result['seq'] += r.get()[1]  # sequence
            rv_result['qual'] += r.get()[2]  # quality score
            rv_result['comp'] += r.get()[3]  # complement sequence

    del jobs_fw, jobs_rv

    pool_fw.close()
    pool_rv.close()
    fastq_df = create_dask_dataframe(fw_result, rv_result)
    del fw_result, rv_result
    return fastq_df


def extend_dataframe(fastq_df):
    """
    extend the dataframe by calculating aditional information
    :param fastq_df:
    :return: extended dataframe
    """
    # check if sequences are paired
    fastq_df['paired'] = fastq_df[['fw_seq', 'rv_seq']].notnull().all(axis=1)
    # get the length of the forward sequence
    fastq_df['fw_seq_length'] = fastq_df['fw_seq'].str.len()
    # fill nan values to prevent parquet schema difference
    fastq_df['fw_seq_length'] = fastq_df['fw_seq_length'].fillna(0)
    # get the length of the reverse sequence
    fastq_df['rv_seq_length'] = fastq_df['rv_seq'].str.len()
    # fill nan values to prevent parquet schema difference
    fastq_df['rv_seq_length'] = fastq_df['rv_seq_length'].fillna(0)
    # necessary because fillna creates floats but the normal length are int
    fastq_df['fw_seq_length'] = fastq_df['fw_seq_length'].astype(int)
    # necessary because fillna creates floats but the normal length are int
    fastq_df['rv_seq_length'] = fastq_df['rv_seq_length'].astype(int)
    fw_a = np.around(
        (fastq_df['fw_seq'].str.count('A').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    fw_t = np.around(
        (fastq_df['fw_seq'].str.count('T').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    fw_g = np.around(
        (fastq_df['fw_seq'].str.count('G').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    fw_c = np.around(
        (fastq_df['fw_seq'].str.count('C').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    temp_fw_df = pd.DataFrame({"fw_A_perc": fw_a, "fw_T_perc": fw_t, "fw_G_perc": fw_g, "fw_C_perc": fw_c},
                              index=fastq_df.index.compute())
    fastq_df = fastq_df.merge(temp_fw_df)
    del fw_a, fw_t, fw_g, fw_c, temp_fw_df

    rv_a = np.around(
        (fastq_df['rv_seq'].str.count('A').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    rv_t = np.around(
        (fastq_df['rv_seq'].str.count('T').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    rv_g = np.around(
        (fastq_df['rv_seq'].str.count('G').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    rv_c = np.around(
        (fastq_df['rv_seq'].str.count('C').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(
            np.double),
        4)
    temp_rv_df = pd.DataFrame({"rv_A_perc": rv_a, "rv_T_perc": rv_t, "rv_G_perc": rv_g, "rv_C_perc": rv_c},
                              index=fastq_df.index.compute())
    fastq_df = fastq_df.merge(temp_rv_df)
    del rv_a, rv_t, rv_g, rv_c, temp_rv_df

    return fastq_df


def process_fastq_chunk(filename, chunk_start, chunk_size, is_rev: bool):
    """
    Parse the items in a chunk a fastq file
    :param filename: fastq file
    :param chunk_start: start of the current chunk of the file
    :param chunk_size: size of the current chunk
    :param is_rev: boolean to check if the current chunk come from a reverse sequence
    :return: 4 lists containing the items from the chunk of the fastq file
    """
    with open(filename, 'r') as f:
        f.seek(chunk_start)
        lines = f.read(chunk_size).splitlines()
        seq_list = []
        index_list = []
        q_score_list = []
        complement_list = []
        for line in lines:
            sequence = SEQUENCE_PATTERN.fullmatch(line.rstrip())
            header = HEADER_PATTERN.fullmatch(line.rstrip())
            plus = PLUS_PATTERN.fullmatch(line.rstrip())
            if sequence:
                if is_rev:
                    complement_list.append(get_reverse_complement(line.strip()))
                seq_list.append(line.strip())
                continue
            if header:
                index_list.append(line.strip()[:-2])
                continue
            if plus:
                continue
            else:
                q_score_list.append(line.strip())
        return index_list, seq_list, q_score_list, complement_list


def chunkify(filename, size=1024 * 1024):
    """
    devide a file in multiple chunks of a certain size
    :param filename: file to chunkify
    :param size: size of the chunks
    :return: iterator containing the chunkstart and size
    """
    fileEnd = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        chunkEnd = f.tell()
        while True:
            chunkStart = chunkEnd
            f.seek(size, 1)
            f.readline()
            chunkEnd = f.tell()
            yield chunkStart, chunkEnd - chunkStart
            if chunkEnd >= fileEnd:
                break


def create_dask_dataframe(fw_data, rv_data):
    """
    Creates the dask dataframe
    :param fw_data: dictionary containing fastq items
    :param rv_data: dictionary containing fastq items
    :return: dask dataframe
    """
    fw_columns = ['fw_seq', 'fw_seq_score', 'fw_seq_length']
    fw_df = pd.DataFrame(columns=fw_columns, index=fw_data['index'])

    fw_df['fw_seq'] = fw_data['seq']
    fw_df['fw_seq_score'] = fw_data['qual']
    del fw_data
    ddf = dd.from_pandas(fw_df, npartitions=4)
    del fw_df
    rv_columns = ['rv_seq', 'rvc_seq', 'rv_seq_score', 'rv_seq_length']
    rv_df = pd.DataFrame(columns=rv_columns, index=rv_data['index'])
    rv_df['rv_seq'] = rv_data['seq']
    rv_df['rvc_seq'] = rv_data['comp']
    rv_df['rv_seq_score'] = rv_data['qual']
    del rv_data
    ddf = ddf.join(rv_df, lsuffix='_caller', rsuffix='_other')
    del rv_df

    ddf['flagged'] = False
    ddf['paired_flag'] = False
    ddf['fw_a_perc_flag'] = False
    ddf['fw_t_perc_flag'] = False
    ddf['fw_g_perc_flag'] = False
    ddf['fw_c_perc_flag'] = False
    ddf['rv_a_perc_flag'] = False
    ddf['rv_t_perc_flag'] = False
    ddf['rv_g_perc_flag'] = False
    ddf['rv_c_perc_flag'] = False
    ddf['fw_seq_len_flag'] = False
    ddf['rv_seq_len_flag'] = False
    ddf['identity_flag'] = False
    return ddf
