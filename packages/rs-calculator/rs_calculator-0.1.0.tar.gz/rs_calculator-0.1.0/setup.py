from setuptools import setup, find_packages

setup(
    name="rs_calculator",
    version="0.1.0",
    description="A simple calculator library for python beginners",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Rasa Dariush",
    author_email="your.email@example.com",  # Optional
    url="https://github.com/Rasa8877/rs-calculator.git",  # Optional
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Education",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires='>=3.6',
)
