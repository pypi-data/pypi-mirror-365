from setuptools import setup, find_packages

setup(
    name="fileez",
    version="0.1.0",  # update this on each release
    author="Rasa Dariush",
    author_email="letperhut@gmail.com",
    description="A simple and friendly Python library to handle files and folders",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Rasa8877/fileez",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
