from setuptools import setup

setup(
    name="sqlpoop",
    version="0.2",
    author="Stabosa87",
    author_email="stab@stab.ing",
    description="drop in replacement for sqlite for multi writing using tcp with serialized writes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    py_modules=["sqlpoop"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)