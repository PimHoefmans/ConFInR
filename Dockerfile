FROM python:3.5

WORKDIR /home/yeet
COPY  config.py LICENSE meta_verstand.py README.md requirements.txt /home/yeet/ 
COPY app ./app 
COPY bowtie2-2.2.6-source.zip /home/bowtie2/bowtie2-2.2.6-source.zip 
RUN mkdir data
RUN mkdir data/Bowtie2_data
RUN mkdir data/Bowtie2_data/fasta
RUN mkdir data/Bowtie2_data/index
RUN mkdir data/Bowtie2_data/output
RUN apt-get update
RUN apt-get install unzip 
RUN unzip /home/bowtie2/bowtie2-2.2.6-source.zip
RUN mv bowtie2-2.2.6 /home/bowtie2/

WORKDIR /home/bowtie2/bowtie2-2.2.6
RUN make 
RUN apt-get update
RUN apt-cache search tbb
RUN apt-get install libtbb-dev -y
ENV PATH=$PATH:/home/bowtie2/bowtie2-2.2.6
RUN export PATH

WORKDIR /home/yeet
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
ENV FLASK_APP meta_verstand.py


EXPOSE 5000
CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "--workers=13", "--threads=6", "meta_verstand:app"]
