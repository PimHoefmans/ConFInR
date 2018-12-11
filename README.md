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

### Set environment variable
To ensure that ConFInR can efficiently handle data throughout your system, please store the path to the ConFInR folder in an environment variable:
```$ export CONFINR_PATH=/path/to/confinr/folder```

## Usage

### Executing ConFInR from the command line
After following the installation steps above, specific ConFInR functions can be executed directly from the command line. The commands including descriptions, parameters and code examples are listed below.

#### confinr-preprocess
Given a .tsv file, this function extracts sequences and converts to FASTA format.

| Parameter | Description |
| :-------- | :---------- |
| --i       | Path to input file (.tvs)     |
| --o       | Path to output file (.fasta)  |

Code example: ```$ confinr-preprocess --i table.tsv --o sequences.fasta```


#### confinr-makedb
Given a protein reference database file (.fasta), this function creates a DIAMOND database in the REFERENCE folder. 

| Parameter | Description |
| :-------- | :---------- |
| --d       | Path to the output DIAMOND database file (no file extension needed) |
| --i       | Path to the input protein reference database file (.fasta)          |

Code example: ```$ confinr-makedb --d database --o database.fasta```


#### confinr-run
Given an input file (.fasta), this function runs DIAMOND in BLASTX mode and stores the output in a run folder.

| Parameter | Description |
| :-------- | :---------- |
| --d       | Path to the DIAMOND database file                                     |
| --q       | Path to the query input file                                          |
| --params  | Optional DIAMOND parameters, surround multiple parameters with quotes |

Code example: ```$ confinr-run --d database --q sequences.fasta --params '--sensitive --matrix PAM250'```


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
        └── output.m8
```

## Credits

## License
