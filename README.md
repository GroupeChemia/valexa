# Valexa
[![Build Status](https://travis-ci.org/GroupeChemia/valexa.svg?branch=master)](https://travis-ci.org/GroupeChemia/valexa)

## What is it?

Valexa is an analytical method validation library. It uses accuracy profile as described in 
[Hubert et Al., 2006](https://www.sciencedirect.com/science/article/abs/pii/S0731708504003292). The profiles are 
generated with [Numpy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/), 
[Shapely](https://github.com/Toblerity/Shapely) is used to find the validation limit of the profile. Models are managed
with [Sympy](https://www.sympy.org/) and [Statsmodels](https://www.statsmodels.org/).

Valexa aims to be modular and versatile. It can be used stand alone or included in larger project.

## How to use it?

### Installation

Valexa use [Poetry](https://python-poetry.org/) as a package manager.

    pip install poetry
    
    poetry install
    
    poetry shell
    
    nodeenv -p
    
    npm install
    
Si une erreur 'undefined ls-remote -h -t ssh: ...' apparait avec la commande 'npm install', télécharger 
[Git For Windows](https://gitforwindows.org/) et l'installer.
    
### How to use

The current version does not have any gui yet. To generate the profile, modify the main.py to suits your needs. Look at
'tests/data/test_dataset.py' for more detail on the data format needed.

To run the Electron GUI type:

    npm run electron:serve
