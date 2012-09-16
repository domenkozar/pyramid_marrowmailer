#!/bin/bash
# TODO: stash changes before doing tests: http://codeinthehole.com/writing/tips-for-using-a-git-pre-commit-hook/

function handle_exit {
    if [ $? -ne 0 ]; then
        EXITCODE=1
    fi
}

echo '====== Running tests ========='
bin/nosetests; handle_exit

echo '====== Running PyFlakes ======'
bin/python setup.py flakes; handle_exit

echo '====== Running pep8 =========='
bin/pep8 src/pyramid_marrowmailer; handle_exit
bin/pep8 *.py; handle_exit
