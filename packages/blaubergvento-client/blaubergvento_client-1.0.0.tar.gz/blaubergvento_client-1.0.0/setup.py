"""
Setup of the blauberg vento module
"""
from setuptools import setup

setup(
    name="blaubergvento_client",
    version="1.0.0",
    description="Client for Blauberg Vento and derived ventilators",
    long_description=(
        "This is a Python module for communicating with a Blauberg Vento (and OEMS like Duka One S6w). The Blauberg Vento is a one room ventilationsystem with a heat exchanger."
        "This module has roots in the dukaonesdk but has been rewritten from scratch in order to better seperate reponsibilites into different classes, while still being able to reuse shared logic."
        "The primary goal for this module is to create a Python client that makes communicating with Blauberg Vento(and its derivatives) a simple task."
    ),
    author="Michael Krog",
    url="https://github.com/michaelkrog/blaubergvento-python",
    packages=["blaubergvento_client"],
    license="GPL-3.0",
)