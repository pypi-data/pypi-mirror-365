from setuptools import setup, find_packages

setup(
    name="nats-fasterapi",
    version="0.2.1",
    description="A CLI tool to scaffold FastAPI projects with CRUD and schema support",
    author="Nathaniel Uriri",
    author_email="nat@uriri.com.ng",

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "click",
        "pymongo",
        "pydantic",
        "fastapi[all]",
        "motor",
        "redis",
        "requests",
        "pyjwt",
        "python-dotenv",
    ],

    entry_points={
        "console_scripts": [
            "fasterapi=fasterapi.cli:cli",
        ],
    },

    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    python_requires=">=3.8",
)
