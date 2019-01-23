# ConFInR

## Desciption
The ConFInR tool is a Python tool used for functional annotation of nucleotide sequences from metagenomics experiments. It takes a given input of various files, such as fastq, tsv or fasta files, and, using a database of choice, executes it against DIAMOND, a high performance sequence aligner, to align proteins to them and in turn annotate the protein's functions to the nucleotide sequences in another web-tool.

#### This is the web-application version, please switch to the [command-line-release](https://github.com/kjradem/ConFInR/tree/cl-release) for the command-line version of this application

## Table Of Contents
* [Description](https://github.com/kjradem/ConFInR/tree/cl-release/README.md#description)
* [Table Of Contents](https://github.com/kjradem/ConFInR/tree/cl-release/README.md#table-of-contents)
* [Installation](https://github.com/kjradem/ConFInR/tree/cl-release/README.md#installation)
* [Usage](https://github.com/kjradem/ConFInR/tree/cl-release/README.md#usage)
* [Credits](https://github.com/kjradem/ConFInR/tree/cl-release/README.md#credits)
* [License](https://github.com/kjradem/ConFInR/tree/cl-releasee/LICENSE)

## Installation

#### Pre-requisites
1. Ensure that Python 3 is installed, including pip (which should be by default).

#### Diamond

1. Install DIAMOND from the [Git repository](https://github.com/bbuchfink/diamond) and extract the binary file:

`wget http://github.com/bbuchfink/diamond/releases/download/v0.9.23/diamond-linux64.tar.gz`

`tar xzf diamond-linux64.tar.gz`

2. Move the binary file _diamond_ to a directory contained in your executable search path (PATH environment variable):

`(sudo) mv diamond /usr/bin`

#### ConFInR

1. Clone the ConFInR web version and switch to the web version release:

`(sudo) git clone https://github.com/kjradem/ConFInR.git`

`(sudo) git checkout webapp-release`

2. Set up a virtual environment with virtualenv:

`(sudo) virtualenv -p python3 venv`

3. Activate the virtual environment

`source venv/bin/activate`

4. Install the dependencies in the virtual environment:

`(sudo) pip3 install -r requirements.txt`

5. Set up Flask

`export FLASK_APP=webapp.py`

6. Run the application

`flask run`

7. Go to the appropriate web address

`127.0.0.1:5000/`

8. Deactivate the virtual environment once you're done

`deactivate`

## Usage

**Please ensure that all [installation steps](https://github.com/kjradem/ConFInR/wiki/Installation-(web-application)) have been completed.**

In order to use ConFInR on the internet, simply start up your internet browser and go to [the ConFInR site](http://127.0.0.1:5000/).

Afterwards, select your Query file and Database file in their appropriate format. The compatible formats for the query file are FASTA, FASTQ or TSV formats. (These formats are also allowed while Zipped.) The file for the database can be either a pre-built DMND file or a FASTA file.

Once these files are selected, press the Upload button. Once this progress is finished, you can Run Diamond.
You can Run Diamond normally, or have a more specialized run of Diamond using the Advanced Parameters.
These parameters are further explained down below. 

Once Diamond is done running, you can download the output using the Download output button, located next to the Advanced Parameters and Run Diamond buttons    

## Advanced Parameters

You can also further customize the parameters ConFInR uses, in order to do this simply press on the Advanced Parameters button placed below the submit and run buttons.

After clicking, you will see a number of options available for customization, these parameters will be explained further down.

#### Sensitivity
The available options are No extra sensitivity, sensitive and more sensitive.

**- No extra sensitivity:** The default mode and is mainly designed for short read alignment, i.e. finding
significant matches of >50 bits on 30-40aa fragments.

**- sensitive:** This mode is a lot more sensitive than the default and generally recommended for aligning
longer sequences.

**- more sensitive:** This mode provides some additional sensitivity compared to the sensitive mode.

#### Frameshift
This parameter is used for the penalty for frameshifts in DNA-vs-protein alignments. Values around 15 are reasonable for this parameter. Enabling this feature will have the aligner tolerate missing bases in DNA sequences and is most recommended for long, error-prone sequences. In the pairwise output format, frameshifts will be indicated by \ and / for a shift by +1 and -1 nucleotide in the direction of translation respectively.
Note that this feature is disabled by default.

#### Gap open
Parameter for the penalty of opening a gap. 

#### Gap extend
Parameter for the penalty of extending a gap. 

#### Matrix
Parameter used to select the matrix you wish to use.

#### Algorithm
Paramter for the algorithm for seed search. Either double-indexed or query-indexed. The  double-indexed algorithm is the program’s main algorithm, but it is inefficient for very small query files, where the query-indexed algorithm should be used instead. By default, the program will automatically choose one of the algorithms based on the size of
the query and database files. Note that while the two algorithms are configured to provide roughly the same sensitivity for the respective modes, results will not be exactly identical to each other.

#### Outformat
Parameter used to select the format for the output file.

#### Compress
Parameter used to enable compression of the output file. by default there is no compression, alternatively the output file will be zipped by Gzip compression.

#### Max target sequences
Parameter for the maximum number of target sequences per query to report alignments for. The default value is 25.
Setting this to 0 will report all alignments that were found.

#### Min score
Parameter used for the minimum bit score to report an alignment. 
Note that setting this option will override the e-value parameter.

#### ID
Parameter used to filter the alignments below the given percentage of sequence identity. Only values above the given percentage will be shown.

#### Query cover
Parameter used to filter the alignments below the given percentage of query cover. Only values above the given percentage will be shown.

#### Subject cover
Parameter used to filter the alignments below the given percentage of subject cover. Only values above the given percentage will be shown.

#### Max HSPs
Parameter for the maximum number of High scoring segment pairs (HSPs) per subject sequence to report for each query. Note that in general any number of HSPs may exist for a single query/subject pair. The program’s default policy is to report any HSP if its query and subject ranges are not enveloped by a higher scoring HSP and if it meets the e-value treshold. This option may be used to limit the number of HSPs reported. Setting this option to 1 will cause only the single best HSP for each query/subject pair to be reported.

#### Database
Currently the only database you can select is the NR database from NCBI

## Credits
Our team consists of the following members:
* [Sjors](https://github.com/Diadoom)
* [Hidde](https://github.com/HH-Dijkstra)
* [Daan](https://github.com/DaanJG98)
* [Pim](https://github.com/PimHoefmans)
* [Koen](https://github.com/kjradem)
* [Thijs](https://github.com/thijschanka)

## License
This project is licensed under the MIT license, see [LICENSE](https://github.com/kjradem/ConFInR/tree/cl-release/LICENSE) for details.
