import os
import re
import multiprocessing as mp
from app.core.objects.FastQData import FastQData
from app.core.objects.FastQDataframe import FastQDataframe
from app.core.utils.preprocess_utils import get_reverse_complement
from app.core.preprocessing.calculations import get_nucleotide_percentages, get_paired_reads, get_sequence_length


SEQUENCE_PATTERN = re.compile("^[ATGCNYPatgcnyp]+")
HEADER_PATTERN = re.compile("^@.*HWI.+(:\d+){3,10}.+")
PLUS_PATTERN = re.compile("^\+")


def preprocess_fastq_files_mp(fw_file, rv_file, uuid: str):
    fastq_df = initialize_dataframe(uuid, fw_file, rv_file)
    extend_dataframe(fastq_df.get_dataframe())
    fastq_df.to_pickle(path='data/' + uuid + '/', filename='pickle')


def initialize_dataframe(uuid, fw_file, rv_file):
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
    # fw_data = FastQData(fw_result['index'], fw_result['seq'], fw_result['comp'], fw_result['qual'], False)
    # rv_data = FastQData(rv_result['index'], rv_result['seq'], rv_result['comp'], rv_result['qual'], True)
    fastq_df = FastQDataframe(fw_dict=fw_result, rv_dict=rv_result, df_id=uuid)
    del fw_result, rv_result
    return fastq_df


def extend_dataframe(fastq_df):
    get_paired_reads(fastq_df)
    get_nucleotide_percentages(fastq_df, "fw_")
    get_nucleotide_percentages(fastq_df, "rv_")
    get_sequence_length(fastq_df)


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
