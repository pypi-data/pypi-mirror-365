from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import glob
import os
import pkg_resources

# Get version without importing the module
import os
import re

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'snipit', '__init__.py')
    with open(version_file, 'r') as f:
        content = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

def get_program_name():
    version_file = os.path.join(os.path.dirname(__file__), 'snipit', '__init__.py')
    with open(version_file, 'r') as f:
        content = f.read()
        program_match = re.search(r"^_program = ['\"]([^'\"]*)['\"]", content, re.M)
        if program_match:
            return program_match.group(1)
        raise RuntimeError("Unable to find program name.")

__version__ = get_version()
_program = get_program_name()

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='snipit-mc',
      version=__version__,
      packages=find_packages(),
      scripts=["snipit/scripts/snp_functions.py"],
      install_requires=[
            "biopython>=1.70",
            "matplotlib>=3.2.1"
        ],
      description='Enhanced snipit with artistic color palettes and improved SNP visualization',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/hyzhou1990/snipit-multicolor',
      author='hyzhou1990',
      author_email='',
      license='GPL-3.0',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
          "Topic :: Scientific/Engineering :: Visualization",
      ],
      entry_points="""
      [console_scripts]
      {program} = snipit.command:main
      """.format(program = _program),
      include_package_data=True,
      keywords=[
          "bioinformatics",
          "snp",
          "visualization",
          "genomics",
          "mutation",
          "phylogenetics",
          "sequence-analysis",
          "covid",
          "sars-cov-2",
          "genbank"
      ],
      python_requires=">=3.7",
      zip_safe=False,
      project_urls={
          "Bug Reports": "https://github.com/hyzhou1990/snipit-multicolor/issues",
          "Source": "https://github.com/hyzhou1990/snipit-multicolor",
          "Documentation": "https://github.com/hyzhou1990/snipit-multicolor#readme",
      })
