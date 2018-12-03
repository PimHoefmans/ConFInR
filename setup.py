from setuptools import setup


def read_file(file_path):
    with open(file_path, 'r+') as f:
        return f.read()


# TODO: Fix setup to enable command line executability.
# setup(
#     name='ConFInR',
#     version='',
#     description='ConFInR is a Python tool for functional annotation of metagenomics sequences.',
#     long_description=read_file('README.md'),
#     author='Koen Rademaker',
#     author_email='koenrademaker@outlook.com',
#     url='https://github.com/kjradem/ConFInR',
#     py_modules=['confinr'],
#     license=read_file('LICENSE'),
#     entry_points={
#         'console_scripts': [
#             'confinr-init = confinr:initialize',
#             'confinr-preprocess = confinr:preprocess',
#             'confinr-run = confinr:run'
#         ]
#     }
# )
