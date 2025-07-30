# How to create and publish a Python library, Github + Pypi + Pdoc

In this article, I am going to show you how to deploy a simple Python library as an open source project supporing installation via `pip`, Github CI/CD and the documentation.

## Step 1. Create your Python library

Let the library be called `pylib25`. Do not ask me why `25` - it is because `5*5=25`. So first, we create a folder `pylib25` with the following structure:

```
- pylib25/
    - .github
        - workflows
            - publish.yml
    - docs/
    - pylib25/
        - __init__.py
    - .gitignore
    - README.md
    - setup.py
    - tests.py
```

Of course, the structure may be more complicated depending on the complexity of your project. But what is important is that the code of the library is located in its own package (inner `pylib25` in our example) and also we keep `README.md`, `setup.py`, `tests.py`, `.gitignore` in the root. We also do not consider the case for non-python files, dependencies on other libraries or some other extra stuff, because simpler our project is easier to understand and remember the deploy specifics.

## Step 2. Write the code

Now we write a function in `__init__.py` this way:

```python
"""
`pylib25` is a simple library to illustrate how to deploy a Python library.
"""

def sqr(x: float) -> float:
    """
    Get square of the given `x`.

    ```
    from pylib25 import sqr

    assert sqr(5.0) == 25.0
    ```
    """
    return x ** 2
```

Here is the function `sqr` that is public and supposed to be used from the outside. It includes the annotation and doc-string so the documentation page will contain this information. Also we added the doc-string to the whole library. Normally, it can be the same as `README.md`.

## Step 3. Add unit tests

Since we are good guys, we are to test what we just implemented. To do this we add this code to `tests.py`:

```python
from unittest import TestCase

from pylib25 import sqr


class Test(TestCase):
    def test_sqr(self):
        self.assertEqual(sqr(5.0), 25.0)
```

The test command is: `python -m unittest tests`. Try it to check there is no typo in the code. The result must be `OK` if everything is really OK. We do not use `pytest` or other extremely convenient ways for testing because we decided avoiding external dependencies. Since Python has built-in `unittest` module, it should be enough for our small example library.

## Step 4. Write setup.py

Once we cared of the code and the tests, it is time to make the library installable. The easiest way to do it is to write `setup.py` this way:

```python
from setuptools import setup


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='pylib25',
    version="0.1.0",
    author='Alexander Khlebushchev',
    description="A simple library to illustrate how to deploy a Python library..",
    url="https://github.com/fomalhaut88/pylib25",
    project_urls={
        "Homepage": "https://pypi.org/project/pylib25/",
        "Documentation": "https://fomalhaut88.github.io/pylib25/",
        "Source": "https://github.com/fomalhaut88/pylib25",
        "Issues": "https://github.com/fomalhaut88/pylib25/issues",
    },
    packages=['pylib25'],
    license="MIT",
    zip_safe=False,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    python_requires='>=3.12',
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
```

In order to check whether it works as expected, it is recommended to follow these steps to install it in a separate place.

1. Create a new folder `pylib25-example` somewhere.
2. Inside it create a new Python virtualenv: `python -m virtualenv .venv`
3. Activate the virtualenv: `source .venv/bin/activate` (or `.venv/Scripts/activate`)
4. Install the library via PIP: `pip install -U path/to/pylib25`
5. Create a script `main.py` with the following content:

```python
from pylib25 import sqr
print(sqr(5.0))
```

6. Run the script: `python main.py`

You will see `25.0` in the end if everything is correct. Please note that in `setup.py` you should specify the author, URLs and other parameters correctly for your particular case. You need to have Github (https://github.com/) and Pypi (https://pypi.org/) accounts to proceed. Obviously, my author name is `Alexander Khlebushchev` and username is `fomalhaut88`, so in your case there will be something yours.

## Step 5. Publish on Github

If you do not have a Github (https://github.com/) account, create one to continue.

Before publishing, we should specify some files to ignore (in `.gitignore`): some caches, temporary files, etc. Commonly, we ignore the folders `__pycache__`, `build`, `dist` and `egg-info` because they are auxiliary and generated automatically for your platform and Python version. So `.gitignore` may look like this:

```
__pycache__/
/build/
/dist/
/*.egg-info/
```

Also you may need to fill `README.md`. It is time to do it maybe in a brief way so the published page will not look too blank.

After that we should follow these steps:

1. Create a new repository in Github (we choose a public one so we will have Github documentation later) called `pylib25` in our case.
2. Initialize Git in our project: `git init`
3. Make an initial commit: `git add .` and `git commit -am "Initial commit"`
4. Specify the remove repository: `git remote add origin git@github.com:fomalhaut88/pylib25.git`
5. Push the changes to Github: `git push -u origin master`

Once it is done, the code will appear on Github by the link https://github.com/fomalhaut88/pylib25 in our case.

## Step 6. CI/CD and publish on Pypi

[Pypi](https://pypi.org/) is a standard place where Python libraries live, each one can be installed using `pip` by the name (for our case: `pip install pylib25`). If you do not have an account there, create one.

On Pypi in your "Account settings" find the section "API tokens" and create a new token called `PYPI_API_TOKEN`, its value must be something like `pypi-...`. After that, on Github in the project "Settings" find "Secrets and variables" -> "Actions" and add "New repository secret" called `PYPI_API_TOKEN` and the value you just received on Pypi (started with `pypi-`). Once you did it, Github will get the access to publish projects on Pypi.

Now we are ready to create a workflow adding the file `.github/workflows/publish.yml` with the following content:

```
name: Publish Python distributions to PyPI

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  build-n-publish:
    name: Build and publish to PyPI
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Install build dependencies
        run: python -m pip install --upgrade pip setuptools wheel

      - name: Run unittests
        run: python -m unittest tests

      - name: Build binary wheel and a source tarball
        run: python setup.py sdist bdist_wheel

      - name: Publish distribution to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: ${{ secrets.PYPI_API_TOKEN }}
```

After adding this file and pushing it to the repository, view "Actions" on Github. A new action will start to process. It may take a while, when it finishes. On success, you will see the library on Pypi (in our case by the URL https://pypi.org/project/pylib25/). On fail, you can click on the action to view the log and fix the error.

## Step 7. Documentation on Github

One simple way to generate documentation is [pdoc](https://pypi.org/project/pdoc/). First, you need to install it locally using `pip install pdoc`. After that you can generate the documentation from Python doc-strings by the command `pdoc pylib25 -o docs`, so the folder `docs` will appear in the root having the necessary HTML content. You can open `index.html` locally in your browser to view the result. And do not forget to push `docs` to Github in the end.

Now we are to deploy it to a public endpoint. Fortunately, Github provides this opportunity in "Settings" -> "Pages". In the section "Build and deployment" choose the source as "Deploy from a branch" and specify the branch `master` and the folder `docs`. After a while the documentation will be deployed (in our case by the URL https://fomalhaut88.github.io/pylib25/).

## Conclusion

We considered how to publish a Python library, covering Github, Pypi and documentation with Pdoc. Of course, this tutorial is quite limited and in real projects you may need a lot of improvements. But what we've done still can be a good point to start adding new features one by one during the development process. Good luck!
