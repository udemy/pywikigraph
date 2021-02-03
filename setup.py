import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup_args = dict(
    name="pywikigraph",
    version="0.0.1",
    author="Sam Cohan, Raka Dalal, UdemyData",
    author_email="raka.dalal@udemy.com",
    keywords=[
        "Graph Traversal",
        "WikiGraph",
        "Wikipedia Graph",
        "Bidirectional Search",
    ],
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

install_requires = ["scipy"]

if __name__ == "__main__":
    setuptools.setup(**setup_args, install_requires=install_requires)
