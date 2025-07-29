# fileez

[![Python package](https://img.shields.io/pypi/v/fileez.svg)](https://pypi.org/project/fileez/)
[![Build Status](https://github.com/Rasa8877/fileez/actions/workflows/python-package.yml/badge.svg)](https://github.com/Rasa8877/fileez/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**fileez** is a beginner-friendly Python library that makes file and folder handling easier with a clean and simple API.

## Features

- Read/write files (text, JSON, CSV)
- List directories
- Copy, move, or delete files and folders
- UTF-8 encoding by default

## Installation

```bash
pip install fileez
```

## Example

```python
import fileez as fz

fz.write("hello.txt", "Hello, World!")
print(fz.read("hello.txt"))

data = {"name": "fileez", "version": 1}
fz.write_json("data.json", data)
print(fz.read_json("data.json"))

rows = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
fz.write_csv("data.csv", rows)
print(fz.read_csv("data.csv"))
```

## License

MIT