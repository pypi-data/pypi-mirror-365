from setuptools import setup, find_packages

setup(
    name="helloworld-goofy",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author="Legendry Goofy",
    author_email="godmoddev@gmail.com",
    description="A goofy hello world package",
    long_description="Just a fun PyPI test package",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
