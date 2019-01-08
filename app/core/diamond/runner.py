import os
import click
from subprocess import call
from datetime import datetime


CONFINR_PATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
RUN_FOLDERS = ['OUTPUT', 'ANNOTATION']
METADATA_FILE = 'metadata.txt'


def initialize_run():
    """Initialize a ConFInR run by creating the required folder structure.

    Generate a run_id based on the date and time.
    Create defined run folders inside folder named after run_id.
    :raises OSError: If there is no such file or directory to create folders in.
    :return: Run folder name.
    """
    t = datetime.now()
    run_id = '_'.join(['RUN', '-'.join([str(t.day), str(t.month), str(t.year)]),
                       ''.join([str(t.hour) + 'h', str(t.minute) + 'm', str(t.second) + 's'])])
    run_id_folder = '/'.join((CONFINR_PATH, run_id))
    try:
        if not os.path.exists(run_id_folder):
            os.makedirs(run_id_folder)
            os.chdir(run_id_folder)
            for folder in RUN_FOLDERS:
                os.makedirs(folder)
            os.chdir('..')
        return run_id
    except OSError:
        raise OSError


def make_diamond_db(uuid: str):
    """Run DIAMOND's makedb function in command line.

    Create DIAMOND command with input and database to be executed.
    Run DIAMOND command in shell.
    :param uuid: Session id.
    """
    input_file = 'data/' + uuid + '/diamond/database' + 'db.fasta'
    database_file = 'data/' + uuid + '/diamond/database' + 'db.dmnd'
    command = 'diamond makedb --in ' + input_file + ' -d ' + database_file
    call(command, shell=True)


def run_diamond(d: str, q: str, run_id: str, params=None):
    """Run DIAMOND in BLASTX mode in command line.

    Resolve paths for output and database.
    Create DIAMOND command with database, query- and output file to be executed.
    Optionally, append parameters to command.
    Run DIAMOND command in shell.
    :param d: Path to DIAMOND database file.
    :param q: Path to query input file.
    :param run_id: Run folder name.
    :param params: Optional DIAMOND parameter(s), multiple should be surrounded with quotes.
    """
    o = '/'.join((CONFINR_PATH, run_id, 'OUTPUT/matches.m8'))
    if not os.path.exists(d):
        d = '/'.join((CONFINR_PATH, 'REFERENCE', d))
    command = 'diamond blastx -d ' + d + ' -q ' + q + ' -o ' + o
    if params is not None:
        command += ' '+params
    call(command, shell=True)


@click.command()
@click.argument('d')
@click.argument('q')
@click.option('--params', default=None, help='Optional DIAMOND parameters.')
def run_confinr(d: str, q: str, params: str):
    """Perform a ConFInR run; initialize run folder, run DIAMOND and write metadata file.

    :param d: Path to DIAMOND database file.
    :param q: Path to input query file.
    :param params: Optional DIAMOND parameter(s), multiple should be surrounded with quotes.
    """
    run_id = initialize_run()
    run_diamond(d, q, run_id, params)
    write_metadata(q=q, d=d, p=params, run_id=run_id)


def write_metadata(q=None, d=None, p=None, run_id=None):
    """Write metadata file for ConFInR run that includes query file, database and parameters.

    :param q: Path to query file.
    :param d: Path to DIAMOND database.
    :param p: Optional DIAMOND parameters.
    :param run_id: Run folder name.
    :raises OSError: If there is no such file or directory to create a file in.
    """
    try:
        with open('/'.join((CONFINR_PATH, run_id, METADATA_FILE)), 'a+') as f:
            if q is not None:
                f.write('Query file:\t' + q + '\n')
            if d is not None:
                if not os.path.exists(d):
                    d = '/'.join((CONFINR_PATH, 'REFERENCE', d))
                f.write('DIAMOND database:\t' + d + '\n')
            if p is not None:
                f.write('DIAMOND parameters:\t' + p.replace(' -', ', -') + '\n')
    except OSError:
        raise OSError
