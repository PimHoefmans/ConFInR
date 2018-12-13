# ConFInR

## Description
ConFInR is yet another metagenomics Python tool for functional annotation of metagenomics sequences. This is done by using the output from the preprocessing application: YEET. This file is then converted to a fasta file for further processes. A diamond database is created using a database file placed in the according folder. The fasta file is blasted against this diamond database to find the matches of the sequences


## Table Of Contents
* [Description](https://github.com/kjradem/ConFInR/blob/master/README.md#description)
* [Table Of Contents](https://github.com/kjradem/ConFInR/blob/master/README.md#table-of-contents)
* [Installation](https://github.com/kjradem/ConFInR/blob/master/README.md#installation)
* [Usage](https://github.com/kjradem/ConFInR/blob/master/README.md#usage)
* [Credits](https://github.com/kjradem/ConFInR/blob/master/README.md#credits)
* [License](https://github.com/kjradem/ConFInR/blob/master/LICENSE)

## Installation

#### Pre-requisites
1. Ensure that Python 3 is installed, including pip (which should be by default).
2. Install virtualenv:

`(sudo) pip3 install virtualenv`

#### DIAMOND
1. Install DIAMOND from the [Git repository](https://github.com/bbuchfink/diamond) and extract the binary file:

`wget http://github.com/bbuchfink/diamond/releases/download/v0.9.23/diamond-linux64.tar.gz`

`tar xzf diamond-linux64.tar.gz`

2. Move the binary file _diamond_ to a directory contained in your executable search path (PATH environment variable):

`(sudo) mv diamond /usr/bin`

#### ConFInR
1. Clone the ConFInR repository and switch to the command-line branch:

`(sudo) git clone https://github.com/kjradem/ConFInR.git`

`(sudo) git checkout cl-release`

2. Set up a virtual environment with virtualenv:

`(sudo) virtualenv -p python3 venv`

3. Activate the virtual environment:

`source venv/bin/activate`

4. Install dependencies in the virtual environment:
`(sudo) pip3 install --editable .`

5. You can now use ConFInR in the command line, see [Usage](https://github.com/kjradem/ConFInR/blob/master/README.md#usage) for details on this. After usage you can deactivate your virtual environment with:

`deactivate`

## Usage

### Executing ConFInR from the command line
After following the installation steps above, specific ConFInR functions can be executed directly from the command line. The commands including descriptions, parameters and code examples are listed below.

#### confinr-convert
Given a .tsv file, this function extracts sequences and converts to FASTA format.

| Parameter | Description           | Optional |
| :-------- | :-------------------- | :------- |
| i         | Path to input file    | No       |
| o         | Path for output file  | Yes      |

Code example: ```$ confinr-convert table.tsv --o sequences.fasta```

#### confinr-makedb
Given a protein reference database file (.fasta), this function creates a DIAMOND database in the REFERENCE folder. 

| Parameter | Description                   | Optional |
| :-------- | :---------------------------- | :------- |
| d         | Path to input file            | No       |
| i         | Path to DIAMOND database file | No       |

Code example: ```$ confinr-makedb database database.fasta```

#### confinr-run
Given an input file (.fasta), this function runs DIAMOND in BLASTX mode and stores the output in a run folder.

| Parameter | Description                                                              | Optional |
| :-------- | :----------------------------------------------------------------------- | :------- |
| d         | Path to DIAMOND database file                                            | No       | 
| q         | Path to query input file                                                 | No       |
| params    | Optional DIAMOND parameter(s), multiple should be surrounded with quotes | Yes      |

Code example: ```$ confinr-run database sequences.fasta --params '--sensitive --matrix PAM250'```

### Folder structure
ConFInR's folder structure is shown below, including an example run folder. Run folders are automatically created when running ConFInR to store results and metadata and are named '_RUN\_[date]\_[time]_'.
```bash
.
├── README.md
├── LICENSE
├── requirements.txt
├── confinr.py
├── setup.pt
├── REFERENCE
│   └── database.dmnd
└── RUN_date_time
    ├── metadata.txt
    ├── ANNOTATION
    │   └── annotation.txt
    └── OUTPUT
        └── matches.m8
```

## Credits

## License
This project is licensed under the MIT license, see [LICENSE](https://github.com/kjradem/ConFInR/blob/master/LICENSE) for details.
