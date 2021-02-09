# pywikigraph

pywikigraph helps you determine the relationship between any two wikipedia articles, bold or italic terms. It tells you how closely they are connected to other (degree of separation) and also the exact shortest paths between them. You have the option to specify whether you want to use a directed graph or an undirected graph.

To learn more about this project and/or its use cases, please take a look at this [blog](https://medium.com/udemy-engineering/fast-wikipedia-traversal-algorithm-and-its-applications-in-nlp-and-keyphrase-extraction-9d6ff4c4a68b).

How to install the package:
----------------------------
`pip install pywikigraph`

How to get the data:
-------------------------
The first time you use the package, data will be automatically downloaded in your specified path. In case, you want to download the data manually. There are two files that needs to be downloaded:
- [wikigraph_directed_csr.npz](http://s3.amazonaws.com/udemy-open-source/pywikigraph/wikigraph_directed_csr.npz)
- [index.pkl](http://s3.amazonaws.com/udemy-open-source/pywikigraph/index.pkl)

How to use the package:
------------------------
```python
>>> from pywikigraph import WikiGraph
>>> wg = WikiGraph(path_to_data)
```
Here `path_to_data` refers to the path you want the data to be downloaded or the path containing the files the `index.pkl` and `wikigraph_directed_csr.npz` in case you manually downloaded them.

To find the degree of separation and the shortest paths between two inputs - *Backpropagation* and *Data Science*:
```python
>>> paths = wg.get_shortest_paths_info('Backpropagation', 'Data Science')
>>> paths
(2, 1, [['backpropagation', 'machine learning', 'data science']])
```
- First element of tuple indicates degree of separation
- Second element of tuple indicates number of shortest paths
- Third element of tuple is a list of exact paths

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
