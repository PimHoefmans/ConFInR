from subprocess import call


def make_diamond_db(uuid: str):
    """Run DIAMOND's makedb function in command line.

    Create DIAMOND command with input and database to be executed.
    Run DIAMOND command in shell.
    :param uuid: Session id.
    """
    input_file = 'data/' + uuid + '/diamond/database/' + 'db.fasta'
    database_file = 'data/' + uuid + '/diamond/database/' + 'db.dmnd'
    command = 'diamond makedb --in ' + input_file + ' -d ' + database_file
    call(command, shell=True)
