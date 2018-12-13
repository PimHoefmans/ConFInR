import re
import os
from app.core.objects.FastQData import FastQData
from app.core.objects.FastQDataframe import FastQDataframe
from app.core.exceptions.exceptions import MissingDataException
from app.core.utils.preprocess_utils import get_reverse_complement
from app.core.preprocessing.calculations import get_nucleotide_percentages, get_paired_reads, get_sequence_length


PATTERN = re.compile("(^@[a-zA-Z0-9_].*\n)([ATGCNYPatgcnyp]*\n)(\+\n)(.+($\n|.))", flags=re.MULTILINE)


def preprocess_fastq_files(fw_file, rv_file, uuid: str):
    fastq_df = initialize_dataframe(uuid, fw_file, rv_file)
    extend_dataframe(fastq_df.get_dataframe())
    fastq_df.to_pickle(path='data/'+uuid+'/', filename='pickle')


def initialize_dataframe(uuid, fw_file, rv_file):
    fw_data = parse_fastq(os.path.abspath(fw_file), False)
    rvc_data = parse_fastq(os.path.abspath(rv_file), True)

    fastq_df = FastQDataframe(fw_data=fw_data, rvc_data=rvc_data, df_id=uuid)
    return fastq_df


def extend_dataframe(fastq_df):
    get_paired_reads(fastq_df)
    get_nucleotide_percentages(fastq_df, "fw_")
    get_nucleotide_percentages(fastq_df, "rv_")
    get_sequence_length(fastq_df)


def parse_fastq(filename: str, is_rev: bool):
    index_list = []
    sequence_list = []
    complement_list = []
    q_score_list = []

    with open(os.path.abspath(filename)) as file_object:
        matches = re.findall(PATTERN, file_object.read())
        for match in matches:
            try:
                if is_rev:
                    q_score_list.append(match[3].strip())
                    sequence_list.append(match[1].strip())
                    complement_list.append(get_reverse_complement(match[1].strip()))
                    index_list.append(match[0].strip()[:-2])
                else:
                    q_score_list.append(match[3].strip())
                    sequence_list.append(match[1].strip())
                    index_list.append(match[0].strip()[:-2])
            except Exception:
                raise MissingDataException('Fastq data is incomplete')
    return FastQData(index_list, sequence_list, complement_list, q_score_list, is_rev)
