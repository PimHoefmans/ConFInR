import os
from Bio import SeqIO
import multiprocessing
import subprocess


def bowtie2_builder(fw_fastq):
    """
    Build the index files for Bowtie2 from forward fastq data.
    :param fw_fastq: Path to forward fastq data file.
    """
    with open(os.path.abspath(fw_fastq)) as f:
        fw_data = SeqIO.parse(f, "fastq")
        fileloc = "data/Bowtie2_data/fasta/fw_data.fasta"
        if not os.path.exists(os.path.dirname(fileloc)):
            os.makedirs(os.path.dirname(fileloc))
        SeqIO.write(fw_data, fileloc, "fasta")
    if not os.path.exists(os.path.dirname("data/Bowtie2_data/index/")):
        os.makedirs(os.path.dirname("data/Bowtie2_data/index/"))
    subprocess.call("bowtie2-build "+ os.path.abspath("data/Bowtie2_data/fasta/fw_data.fasta") + " " + os.path.abspath("data/Bowtie2_data/index/index"), shell=True)

def bowtie2_aligner(fw_fastq, rv_fastq):
    """
    Run Bowtie2 on the command line with forward and reverse fastq data.
    :param fw_fastq: file location forward fastq file
    :param rv_fastq: file location reverse fastq file
    """
    if not os.path.exists(os.path.dirname("data/Bowtie2_data/output/output.sam")):
        os.makedirs(os.path.dirname("data/Bowtie2_data/output/output.sam"))
    threads = multiprocessing.cpu_count() - 2
    print(threads)
    if threads < 1:
        threads = 1
    subprocess.call("bowtie2 -p " + str(threads) + " --local --no-hd --fr --no-mixed -x " + os.path.abspath("data/Bowtie2_data/index/index")
              + " -1 " + os.path.abspath(fw_fastq) + " -2 " + os.path.abspath(rv_fastq) + " -S " + os.path.abspath("data/Bowtie2_data/output/output.sam"), shell=True)
