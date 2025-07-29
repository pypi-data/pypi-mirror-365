from setuptools import setup

setup(
    name="prithvi-py-sdk",
    version="0.1.0",
    description="Official Python SDK for Prithvi in-memory key-value database.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sidharth P",
    author_email="philkhanasidharth14@gmail.com",
    url="https://github.com/psidh/prithvi-py-sdk",
    py_modules=["prithvi_client"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

