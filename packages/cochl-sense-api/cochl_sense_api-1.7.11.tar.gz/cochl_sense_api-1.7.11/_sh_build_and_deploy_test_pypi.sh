#!/bin/sh

echo
grep -r '\.getheader(' ./src
echo

echo 'Is working with python 3.12? (y/n)'
read -r ANSWER0

# echo "${ANSWER0}"

if [ "${ANSWER0}" = "n" ]; then
  exit
fi

echo
echo '[VERSION AT src/cochl_sense_api/__init__.py]'
grep __version__ src/cochl_sense_api/__init__.py

echo

echo '[VERSION AT pyproject.toml]'
grep version pyproject.toml
echo

echo '[VERSION AT README.md]'
grep version README.md
echo

echo 'Do versions match? (y/n)'
read -r ANSWER1

# echo "${ANSWER1}"

if [ "${ANSWER1}" = "n" ]; then
  exit
fi

echo
git status
echo 'All changes are pushed? (y/n)'
read -r ANSWER2

# echo "${ANSWER2}"

if [ "${ANSWER2}" = "n" ]; then
  exit
fi

sudo apt install python3.9
sudo apt install python3.9-venv

python3.9 --version
python3.9 -m pip install --upgrade pip
python3.9 -m pip install --upgrade build

rm -rf dist
mkdir dist
rm -rf .gitignore
rm -rf .idea

python3.9 -m build
git reset --hard

python3.9 -m pip install --upgrade twine

cp -f ~/.test_pypirc ~/.pypirc
python3.9 -m twine upload dist/* --verbose --repository testpypi
rm -rf ~/.pypirc
