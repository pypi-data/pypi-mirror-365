from setuptools import setup, find_packages

setup(
    name="paymob_sdk",
    version="1.0.1",
    packages=find_packages(),
    install_requires=["urllib3"],
    author="Youssef",
    desription="Unofficial Paymob Python SDK for payment processing",
    long_description="An unofficial SDK for integrating Paymob payment services in Python applications.",
    long_description_content_type="text/markdown",
)