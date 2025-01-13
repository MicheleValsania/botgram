from setuptools import setup, find_namespace_packages

setup(
    name="botgram",
    version="0.1",
    packages=find_namespace_packages(include=['src', 'src.*']),
    install_requires=[
        # dependencies are already in requirements.txt
    ],
)