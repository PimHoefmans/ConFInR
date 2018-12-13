# ConFInR

## Description
ConFInR is a Python tool for functional annotation of metagenomics sequences.

## Table Of Contents
* [Description](https://github.com/kjradem/ConFInR/blob/master/README.md#description)
* [Table Of Contents](https://github.com/kjradem/ConFInR/blob/master/README.md#table-of-contents)
* [Installation](https://github.com/kjradem/ConFInR/blob/master/README.md#installation)
* [Usage](https://github.com/kjradem/ConFInR/blob/master/README.md#usage)
* [Credits](https://github.com/kjradem/ConFInR/blob/master/README.md#credits)
* [License](https://github.com/kjradem/ConFInR/blob/master/LICENSE)

## Installation
1. Make sure that the correct python version is installed (<= python 3.6)

2. Make sure virtualenv is installed as well:

`(sudo) pip3 install virtualenv`

3. Clone from the ConFInR repository:

`git clone https://github.com/kjradem/ConFInR.git`

4. Set up a virtual environment with virtualenv:

`virtualenv -p python3 venv`

5. Start up the virtual environment:

`source/ venv/bin/activate`

6. Install all the required Python packages needed to run ConFIGnR:

`pip3 install -r requirements.txt` 

7. Download the database you wish to use for blasting 

(8. Place the database file in the map named REFERENCE) perhaps this step should be done later down the line? 

9. Once you've completed your work, deactivate the virtual environment using the following command

`deactivate`
``
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
