from setuptools import setup, find_packages

setup(
    name="RoManTools",
    version="1.0",
    description="A tool for segmenting, validating, and converting Romanized Mandarin text.",
    author="Jeff Heller",
    author_email="jsheller@princeton.edu",
    url="https://github.com/JHGFD82/RoManTools",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'romantools=main:main'
        ],
    },
    install_requires=[
        "numpy>=1.19.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Linguistic"
    ],
    python_requires=">=3.6"
)
