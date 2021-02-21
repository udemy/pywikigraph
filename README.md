# pywikigraph

pywikigraph helps you determine the relationship between any two wikipedia articles, bold or italic terms. It tells you how closely they are connected to other (degree of separation) and also the exact shortest paths between them. You have the option to specify whether you want to use a directed graph or an undirected graph.

To learn more about this project and/or its use cases, please take a look at this [blog](https://medium.com/udemy-engineering/fast-wikipedia-traversal-algorithm-and-its-applications-in-nlp-and-keyphrase-extraction-9d6ff4c4a68b).

How to install the package:
----------------------------
`pip install pywikigraph`

How to get the data:
-------------------------
This package requires two data files to work. These files take about 1.68 GB on disk and about 8.1 GB in memory. They will be lazily downloaded from s3 to your machine and loaded into memory on your first call to get shortest paths.

The two files are linked below:
- [wikigraph_directed_csr.npz](http://s3.amazonaws.com/udemy-open-source/pywikigraph/wikigraph_directed_csr.npz): a sparse array of directed topic connections.
- [index.pkl](http://s3.amazonaws.com/udemy-open-source/pywikigraph/index.pkl): a pickle file with mappings from topic to index in the sparse matrix.

Note that if you do not specify a data path, the data files will be downloaded to `~/.pywikigraph`.


How to use the package:
------------------------
```python
>>> from pywikigraph import WikiGraph
>>> wg = WikiGraph()
```
Note that by default, the data will be downloaded from s3 and loaded to memory from `~/.pywikigraph` folder on your machine, but you can override this path via the `data_root` parameter at initialization. The instantiation will always be instant as the data download and load-to-memory are done lazily. This means that your first ever call to get shortest paths will take several minutes to download the files and load them into memory. Also, since the files are relatively large (1.68 GB on disk and 8.1 GB in memory), your first call to a newly instantiated  `WikiGraph` object will always take some time to load the files from disk to memory (about 70 seconds on a MacBook Pro with 2.6Ghz CPU and 16 GB RAM). All subsequent calls should be extremely fast though.

To find the degree of separation and the shortest paths between two inputs - *Backpropagation* and *Data Science*:
```python
>>> paths = wg.get_shortest_paths_info('Backpropagation', 'Data Science')
>>> paths
(2, 1, [['backpropagation', 'machine learning', 'data science']])
```
- First element of tuple indicates degree of separation
- Second element of tuple indicates number of shortest paths
- Third element of tuple is a list of exact paths

Again, be prepared for your first ever call to take several minutes to download the data files and load them into memory. If the files are already downloaded, the first call would still take upwards of a minute on most machines to load them into memory. All subsequent calls will be lightning fast though.

If you only care about the number of paths, then you can pass argument `no_paths` and the resulting tuple will just have a None for the paths element.
```python
>>> paths_info = wg.get_shortest_paths_info('Backpropagation', 'Data Science', no_paths=True)
>>> paths_info
(2, 1, None)
```

If you don't care about directionality of the connections, then you can use set directed argument to False:
```python
>>> paths_info = wg.get_shortest_paths_info('Backpropagation', 'Data Science', directed=False)
>>> paths_info
(2,
 5,
 [['backpropagation', 'deep learning', 'data science'],
  ['backpropagation', 'dimensionality reduction', 'data science'],
  ['backpropagation', 'glossary of artificial intelligence', 'data science'],
  ['backpropagation', 'machine learning', 'data science'],
  ['backpropagation', 'tensorflow', 'data science']])
```
