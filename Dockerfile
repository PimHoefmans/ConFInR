FROM python:3.5

WORKDIR /home/ConFInR
COPY  config.py LICENSE webapp.py confinr.py README.md requirements.txt /home/ConFInR/ 
COPY app ./app 
COPY bowtie2-2.2.6-source.zip /home/bowtie2/bowtie2-2.2.6-source.zip 
RUN mkdir REFERENCE
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

WORKDIR /home/diamond
RUN wget http://github.com/bbuchfink/diamond/releases/download/v0.9.23/diamond-linux64.tar.gz
RUN tar xzf diamond-linux64.tar.gz
RUN mv diamond /usr/bin

WORKDIR /home/ConFInR
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
ENV FLASK_APP webapp.py


EXPOSE 5000
CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "--workers=13", "--threads=6", "webapp:app"]
