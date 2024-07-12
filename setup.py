# setup.py

from setuptools import setup, find_packages

setup(
    name='romanization_package',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'romanization=romanization_package.__main__:main',
        ],
    },
)
