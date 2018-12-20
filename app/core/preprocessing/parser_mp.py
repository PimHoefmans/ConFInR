import os
import re
import numpy as np
import pandas as pd
import dask.dataframe as dd
import multiprocessing as mp
from app.core.objects.FastQData import FastQData
from app.core.objects.FastQDataframe import FastQDataframe
from app.core.utils.preprocess_utils import get_reverse_complement
from app.core.preprocessing.calculations import get_nucleotide_percentages, get_paired_reads, get_sequence_length


SEQUENCE_PATTERN = re.compile("^[ATGCNYPatgcnyp]+")
HEADER_PATTERN = re.compile("^@.*HWI.+(:\d+){3,10}.+")
PLUS_PATTERN = re.compile("^\+")


def preprocess_fastq_files_mp(fw_file, rv_file, uuid: str):
    fastq_df = initialize_dataframe(fw_file, rv_file)
    extend_dataframe(fastq_df)
    # fastq_df.to_pickle(path='data/' + uuid + '/', filename='pickle')
    fastq_df.to_parquet('data/'+uuid+'/parquet/')


def initialize_dataframe(fw_file, rv_file):
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
            fw_result['index'] += r.get()[0]
            fw_result['seq'] += r.get()[1]
            fw_result['qual'] += r.get()[2]
            fw_result['comp'] += r.get()[3]
    for r in jobs_rv:
        if r.get():
            rv_result['index'] += r.get()[0]
            rv_result['seq'] += r.get()[1]
            rv_result['qual'] += r.get()[2]
            rv_result['comp'] += r.get()[3]

    del jobs_fw, jobs_rv

    pool_fw.close()
    pool_rv.close()
    fastq_df = create_dask_dataframe(fw_result, rv_result)
    del fw_result, rv_result
    return fastq_df


def extend_dataframe(fastq_df):
    fastq_df['paired'] = fastq_df[['fw_seq', 'rv_seq']].notnull().all(axis=1)
    fastq_df['fw_seq_length'] = fastq_df['fw_seq'].str.len()
    fastq_df['rv_seq_length'] = fastq_df['rv_seq'].str.len()

    fw_a = np.around(
        (fastq_df['fw_seq'].str.count('A').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(np.double),
        4)
    fw_t = np.around(
        (fastq_df['fw_seq'].str.count('T').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(np.double),
        4)
    fw_g = np.around(
        (fastq_df['fw_seq'].str.count('G').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(np.double),
        4)
    fw_c = np.around(
        (fastq_df['fw_seq'].str.count('C').values.compute() / fastq_df['fw_seq_length'].values.compute() * 100).astype(np.double),
        4)
    temp_fw_df = pd.DataFrame({"fw_A_perc": fw_a, "fw_T_perc": fw_t, "fw_G_perc": fw_g, "fw_C_perc": fw_c},
                              index=fastq_df.index.compute())
    fastq_df = fastq_df.join(temp_fw_df)
    del fw_a, fw_t, fw_g, fw_c, temp_fw_df

    rv_a = np.around(
        (fastq_df['rv_seq'].str.count('A').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(np.double),
        4)
    rv_t = np.around(
        (fastq_df['rv_seq'].str.count('T').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(np.double),
        4)
    rv_g = np.around(
        (fastq_df['rv_seq'].str.count('G').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(np.double),
        4)
    rv_c = np.around(
        (fastq_df['rv_seq'].str.count('C').values.compute() / fastq_df['rv_seq_length'].values.compute() * 100).astype(np.double),
        4)
    temp_rv_df = pd.DataFrame({"rv_A_perc": rv_a, "rv_T_perc": rv_t, "rv_G_perc": rv_g, "rv_C_perc": rv_c},
                              index=fastq_df.index.compute())
    fastq_df = fastq_df.join(temp_rv_df)
    del rv_a, rv_t, rv_g, rv_c, temp_rv_df

    return fastq_df
    # get_paired_reads(fastq_df)
    # get_nucleotide_percentages(fastq_df, "fw_")
    # get_nucleotide_percentages(fastq_df, "rv_")
    # get_sequence_length(fastq_df)


def process_fastq_chunk(filename, chunk_start, chunk_size, is_rev: bool):
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


def chunkify(filename, size=1024*1024):
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
    fw_columns = ['fw_seq', 'fw_seq_score', 'fw_seq_length', 'fw_A_perc', 'fw_T_perc', 'fw_G_perc', 'fw_C_perc']
    fw_df = pd.DataFrame(columns=fw_columns, index=fw_data['index'])

    fw_df['fw_seq'] = fw_data['seq']
    fw_df['fw_seq_score'] = fw_data['qual']
    del fw_data
    ddf = dd.from_pandas(fw_df, npartitions=4)
    del fw_df

    rv_columns = ['rv_seq', 'rvc_seq', 'rv_seq_score', 'rv_seq_length', 'rv_A_perc', 'rv_T_perc', 'rv_G_perc',
                  'rv_C_perc']
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
