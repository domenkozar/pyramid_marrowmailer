#!/bin/bash
# TODO: stash changes before doing tests: http://codeinthehole.com/writing/tips-for-using-a-git-pre-commit-hook/

set -xe

echo '====== Running tests ========='
nosetests

echo '====== Running PyFlakes ======'
python setup.py flakes

echo '====== Running pep8 =========='
pep8 src/pyramid_marrowmailer
pep8 *.py
