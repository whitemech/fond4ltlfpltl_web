# FOND 4 LTLf / PLTLf website

The website is available on fond4ltlfpltl.diag.uniroma1.it

## Preliminaries

- Install Pipenv
```
pip install pipenv
```

- Install MONA:

  - download from release page:

        wget http://www.brics.dk/mona/download/mona-1.4-18.tar.gz
        tar -xf mona-1.4-18.tar.gz
      
  - Follows the `INSTALL` steps
  - Check the command `mona` works.

## Setup 

Create and activate a new virtual environment using `pipenv`:

```
pipenv --python=python3.7
pipenv shell
```

Install all the locked dependencies:
```
pipenv install
```

To run the app:

```
python fond4ltlfpltl_web.py
```

