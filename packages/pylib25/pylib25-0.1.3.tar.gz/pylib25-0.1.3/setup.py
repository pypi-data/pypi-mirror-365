from setuptools import setup


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='pylib25',
    version="0.1.3",
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
