import os
from Bio import SeqIO
import multiprocessing
import subprocess


#@TODO: excpetion handeling
#@TODO: WEL ECHT DOEN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def bowtie2_builder(fw_fastq):
    """
    builds the index files that are needed for bowtie2 of the fw data file
    :param fw_fastq: location forward fastq file
    :return:
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
    Function to start bowtie2 on the data
    :param fw_fastq: file location forward fastq file
    :param rv_fastq: file location reverse fastq file
    :return:
    """
    if not os.path.exists(os.path.dirname("data/Bowtie2_data/output/output.sam")):
        os.makedirs(os.path.dirname("data/Bowtie2_data/output/output.sam"))
    threads = multiprocessing.cpu_count() - 2
    print(threads)
    if threads < 1:
        threads = 1
    subprocess.call("bowtie2 -p " + str(threads) + " --local --no-hd --fr --no-mixed -x " + os.path.abspath("data/Bowtie2_data/index/index")
              + " -1 " + os.path.abspath(fw_fastq) + " -2 " + os.path.abspath(rv_fastq) + " -S " + os.path.abspath("data/Bowtie2_data/output/output.sam"), shell=True)







