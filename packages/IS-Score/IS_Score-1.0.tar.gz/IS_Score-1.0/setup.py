from setuptools import setup, find_packages

#python .\setup.py sdist bdist_wheel

setup(
    name='IS_Score',
    version='1.0',
    author='Simone Innocente',
    author_email='simoneinnocente98@gmail.com',
    description='Python package for computing the IS-Score for baseline correction evaluation in Raman spectroscopy.',
    #packages=find_packages(exclude=("IS_Score_GUI*",)),
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "ramanspy",
        "matplotlib",
        "seaborn",
        "PyQt5",
        "qtmodern",
        "scipy",
        "findpeaks",
        "orplib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)