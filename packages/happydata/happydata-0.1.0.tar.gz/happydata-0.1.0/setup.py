from setuptools import setup, find_packages

# pip install -m venv venv
# source venv/bin/activate
# pip install pytest
# venv/bin/pytest

# pip install build twine
# python -m build
# python -m twine upload --verbose dist/happydata-0.0.13*
# pip install happydata

setup(
    name='happydata',
    version='0.0.13',
    author="Daqian",
    packages=["happydata"],
    zip_safe=False,
    description='happy data loading,writing, transforming without third party library',
    long_description='happy data loading,writing, transforming without third party library',
    license='MIT',
    keywords=['data', 'data loading', 'data writing', 'data transforming','json','jsonl','gz','lodash'],
    platforms='Independant',
    url='https://github.com/daqiancode/happydata',
)