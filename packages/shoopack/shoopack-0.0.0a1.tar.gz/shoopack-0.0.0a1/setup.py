from setuptools import setup, find_packages

setup(
    name="shoopack",
    version="0.0.0-alpha.1",
    packages=find_packages(),
    install_requires=[
        "pyzmq",
    ],
    author="zygn",
    url="https://github.com/4am-ciss/shoopack",
    description="Unified IPC layer for Pub/Sub messaging",
    python_requires=">=3.8",
)