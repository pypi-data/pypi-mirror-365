# Contributing

If you notice an error, please don't hesitate to open an issue.

## Development setup

```sh
# update
sudo apt update
# install Python 3.11 for ensuring that tests can be run
sudo apt install python3-pip \
  python3.11 python3.11-dev python3.11-distutils python3.11-venv

# check out repo
git clone https://github.com/birdnet-team/birdnet.git
cd birdnet
# create virtual environment
python3.11 -m venv .venv-bn
source .venv-bn/bin/activate
python3.11 -m pip install -e .[dev,litert]
```

## Running the tests

```sh
# first install the tool like in "Development setup"
# then, navigate into the directory of the repo (if not already done)
cd birdnet
# activate environment
source .venv-bn/bin/activate
# run tests
tox
```

Final lines of test result output:

```log
  py311: commands succeeded
  congratulations :)
```
