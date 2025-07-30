from setuptools import setup, find_packages

setup(
    name="convert_time_to_text",
    version="0.3.0",
    packages=find_packages(),
    description="A simple package to convert time to text.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kartheek G P",
    author_email="",
    url="https://github.com/kartheekgp/convert_time_to_text",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
