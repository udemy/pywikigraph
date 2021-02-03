import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="udemy_opensource_publisher",  # Replace with your own username
    version="0.0.1",
    author="UdemyData",
    author_email="raka.dalal@udemy.com",
    description="Find connection between any two wikipedia topics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/udemy/pywikigraph",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.4",
)
