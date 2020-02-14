import setuptools

# https://dzone.com/articles/executable-package-pip-install

'''
py setup.py bdist_wheel
py  -m twine upload dist/*
'''

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='opcodetools',
    version='1.0',
    author="Christopher Cantrell",
    author_email="topherCantrell@gmail.com",
    description="Assemblers and Disassemblers",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/topherCantrell/opcodetools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)