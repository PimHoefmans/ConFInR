from setuptools import setup


def read_file(file_path):
    with open(file_path, 'r+') as f:
        return f.read()


def read_lines(file_path):
    with open(file_path) as f:
        return f.read().splitlines()


# TODO: ADD LICENSE IMPORT
setup(
    name='ConFInR',
    version='0.1',
    description='ConFInR is a Python tool for functional annotation of metagenomics sequences.',
    long_description=read_file('README.md'),
    author='Koen Rademaker',
    author_email='koenrademaker@outlook.com',
    url='https://github.com/kjradem/ConFInR',
    py_modules=['confinr'],
    install_requires=read_lines('requirements.txt'),
    entry_points='''
            [console_scripts]
            confinr-preprocess=confinr:preprocessing
            confinr-run=confinr:run
        '''
)