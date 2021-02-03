"""
WikiGraph Module for finding paths between topics in Wikipedia Graph of topics.
Valid topics include bold and italic terms found in articles.
"""

import os
import pickle
import urllib.request
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple

import scipy.sparse
from scipy.sparse import csc_matrix, csr_matrix


class WikiGraph:
    """
    This module takes as input a source and target wikipage and finds all possible
    shortest paths between the source and the target. The paths can also include bold
    and italics terms that can be found in the Wikipedia pages.
    """

    def __init__(self, data_root: Optional[str] = None, optimize_memory: bool = True):
        """
        Args:
            data_root: Path to local directory containing the following two files:
                `wikigraph_directed_csr.npz`: Directed adjacency matrix (sparse CSR
                format).
                `index.pkl`: Mapping from topic to index in sparse matrix.
            optimize_memory: Whether to trade off about 10% performance in undirected
                searches in exchange for using 2/3 the memory. Note, this does not
                affect the performance of directed searches so it is on by default.
                (default: True)
        """
        self.global_root = "http://s3.amazonaws.com/udemy-open-source/pywikigraph"
        self.data_root: str = data_root
        self._adj_matrix_directed_csr: Optional[csr_matrix] = None
        self._adj_matrix_directed_csc: Optional[csc_matrix] = None
        self._adj_matrix_undirected_csr: Optional[csr_matrix] = None
        self._adj_matrix_undirected_csc: Optional[csc_matrix] = None
        self._optimize_memory: bool = optimize_memory
        self._topic_index_map: Optional[Dict[str, int]] = None
        self._index_topic_map: Optional[Dict[int, str]] = None

    @property
    def adj_matrix_directed_csr(self) -> Optional[csr_matrix]:
        """Directed adjacency matrix of Wikipedia topics in sparse CSR format."""
        if self._adj_matrix_directed_csr is None:
            matrix_path = os.path.join(self.data_root, "wikigraph_directed_csr.npz")
            if not os.path.exists(matrix_path):
                print("Downloading wikigraph_directed_csr.npz")
                urllib.request.urlretrieve(
                    os.path.join(self.global_root, "wikigraph_directed_csr.npz"),
                    matrix_path,
                )
            self._adj_matrix_directed_csr = scipy.sparse.load_npz(
                os.path.join(self.data_root, "wikigraph_directed_csr.npz")
            )
            self._adj_matrix_directed_csc = None
            self._adj_matrix_undirected_csr = None
            self._adj_matrix_undirected_csc = None
        return self._adj_matrix_directed_csr

    @property
    def adj_matrix_directed_csc(self) -> Optional[csc_matrix]:
        """Directed adjacency matrix of Wikipedia topics in sparse CSC format."""
        if self._adj_matrix_directed_csc is None:
            self._adj_matrix_directed_csc = self.adj_matrix_directed_csr.tocsc()
        return self._adj_matrix_directed_csc

    @property
    def adj_matrix_undirected_csr(self) -> Optional[csr_matrix]:
        """Undirected adjacency matrix of Wikipedia topics in sparse CSR format."""
        if self._adj_matrix_undirected_csr is None:
            if not self._optimize_memory:
                self._adj_matrix_undirected_csr = (
                    self.adj_matrix_directed_csr + self.adj_matrix_directed_csr.T
                )
        return self._adj_matrix_undirected_csr

    @property
    def adj_matrix_undirected_csc(self) -> Optional[csc_matrix]:
        """Undirected adjacency matrix of Wikipedia topics in sparse CSC format."""
        if self._adj_matrix_undirected_csc is None:
            if not self._optimize_memory:
                self._adj_matrix_undirected_csc = self.adj_matrix_undirected_csr.tocsc()
        return self._adj_matrix_undirected_csc

    @property
    def topic_index_map(self) -> Dict[str, int]:
        """Dictionary mapping from topic to index in adjacency matrices."""
        if self._topic_index_map is None:
            dictionary_path = os.path.join(self.data_root, "index.pkl")
            if not os.path.exists(dictionary_path):
                print("Downloading index.pkl")
                urllib.request.urlretrieve(
                    os.path.join(self.global_root, "index.pkl"),
                    dictionary_path,
                )
            with open(os.path.join(self.data_root, "index.pkl"), "rb") as f:
                self._topic_index_map = pickle.load(f)
            self._index_topic_map = None
        return self._topic_index_map

    @property
    def index_topic_map(self) -> Dict[int, str]:
        """Dictionary mapping from index in adjacency matrices to topic."""
        if self._index_topic_map is None:
            self._index_topic_map = {v: k for k, v in self.topic_index_map.items()}
        return self._index_topic_map

    def set_graph(self, topic_children_tuples: List[Tuple[str, List[str]]]):
        """Set the internal WikiGraph (useful for testing).

        Args:
            topic_children_tuples: List of tuples where the first element of each
                tuple is a topic and the second element is a list of child nodes.
        """
        self._topic_index_map = {}
        self._index_topic_map = None
        idx = 0
        vertices = []
        for topic, children in topic_children_tuples:
            topic = self.get_standard(topic)
            topic_idx = self._topic_index_map.get(topic)
            if topic_idx is None:
                topic_idx = idx
                self._topic_index_map[topic] = topic_idx
                idx += 1
            for child in children:
                child = self.get_standard(child)
                child_idx = self._topic_index_map.get(child)
                if child_idx is None:
                    child_idx = idx
                    self._topic_index_map[child] = child_idx
                    idx += 1
                vertices.append([topic_idx, child_idx])
        self._adj_matrix_directed_csr = csr_matrix(
            ([1 for _ in range(len(vertices))], list(zip(*vertices))),
            shape=[idx, idx],
        )
        self._adj_matrix_directed_csc = None
        self._adj_matrix_undirected_csr = None
        self._adj_matrix_undirected_csc = None

    def _exists(self, topic: str, verbose=False):
        """Checks whether the topic exists in the graph."""
        topic = self.get_standard(topic)
        if topic not in self.topic_index_map:
            if verbose:
                print(f"topic='{topic}' not found in graph")
            return False
        return True

    def get_standard(
        self,
        topic: str,
    ) -> str:
        return topic.lower()

    def get_shortest_paths_info(
        self,
        source: str,
        target: str,
        directed: bool = True,
        no_paths: bool = False,
        verbose: bool = False,
    ) -> Tuple[int, int, Optional[List[List[str]]]]:
        """Find the (count of) shortest paths between source and target topics.

        We make use of double-ended breath-first search. In each iteration, we will
        alternate between processing the one-hop neighbors from the source or target
        and store them until a set of common nodes are found that can act as bridge
        between source and target. We will then construct paths from source to bridge
        (working backwards from the bridge to be efficient) and paths from bridge to
        target (working forwards as is natural) and then cross-join these to get all
        shortest paths.

        Args:
            source: Valid wikipedia topic to be used as starting point.
            target: Valid wikipedia topic to be used a ending point.
            directed: Whether to look for directed paths or undirected ones.
                (default: True)
            no_paths: return only degrees of separation and count of paths; the third
                element of the resulting triplet (which usually holds a list of
                paths), will be None. Can be up to 20% faster if you only care about
                the count. (default: False)
            verbose: Whether to print diagnostic information.

        Returns:
            Triplet containing [degrees_of_separation, num_paths, paths].
            The paths will be None if `no_paths` is set to True, otherwise, it will be
            a (possibly empty) sorted list of paths.
        """
        source = self.get_standard(source)
        if not self._exists(topic=source, verbose=verbose):
            return (-1, 0, None if no_paths else [])
        target = self.get_standard(target)
        if not self._exists(topic=target, verbose=verbose):
            return (-1, 0, None if no_paths else [])
        if source == target:
            return (0, 1, None if no_paths else [[source]])

        topic_index_map = self.topic_index_map
        index_topic_map = self.index_topic_map
        src_idx = topic_index_map[source]
        tgt_idx = topic_index_map[target]
        src_frontier = set([src_idx])
        tgt_frontier = set([tgt_idx])
        src_visited = set([src_idx])
        tgt_visited = set([tgt_idx])
        if no_paths:
            src_ancestors = defaultdict(int)
            tgt_children = defaultdict(int)
            src_ancestors[src_idx] = 1
            tgt_children[tgt_idx] = 1

            def update_counter(counter, key, inc):
                counter[key] += inc

        else:
            src_ancestors = defaultdict(set)
            tgt_children = defaultdict(set)

        deg_sep = 0
        bridge_topics = set()
        # We will only consider paths with 6 degrees of separation.
        while deg_sep < 6 and not bridge_topics:
            deg_sep += 1
            # Alternate expansion from source and target.
            from_src = bool(deg_sep % 2)
            if from_src:
                # Expand source frontier.
                new_src_frontier = set()
                for topic in src_frontier:
                    unvisited = self._get_children(topic, directed) - src_visited
                    if no_paths:
                        # Number of ways to get to child is sum of number of ways to
                        # get to ancestors.
                        topic_path_count = src_ancestors[topic]
                        _ = [
                            # src_ancestors.update({child: topic_path_count})
                            update_counter(src_ancestors, child, topic_path_count)
                            for child in unvisited
                        ]
                    else:
                        # Otherwise, just keep track of ancestors, so we can rebuild
                        # the path later.
                        _ = [src_ancestors[child].add(topic) for child in unvisited]
                    new_src_frontier |= unvisited
                src_frontier = new_src_frontier
                src_visited |= src_frontier
            else:
                # Expand target frontier.
                new_tgt_frontier = set()
                for topic in tgt_frontier:
                    unvisited = self._get_ancestors(topic, directed) - tgt_visited
                    if no_paths:
                        # Symmetrical to from-source case.
                        topic_path_count = tgt_children[topic]
                        _ = [
                            # tgt_children.update({ancestor: topic_path_count})
                            update_counter(tgt_children, ancestor, topic_path_count)
                            for ancestor in unvisited
                        ]
                    else:
                        _ = [
                            tgt_children[ancestor].add(topic) for ancestor in unvisited
                        ]
                    new_tgt_frontier |= unvisited
                tgt_frontier = new_tgt_frontier
                tgt_visited |= tgt_frontier
            if not src_frontier or not tgt_frontier:
                break
            bridge_topics = src_frontier & tgt_frontier

        if not bridge_topics:
            if verbose:
                print(
                    f"No paths of length <= 6 found between '{source}' and '{target}'"
                )
            return (-1, 0, None if no_paths else [])

        if tgt_idx in bridge_topics:
            return (deg_sep, 1, None if no_paths else [[source, target]])

        if no_paths:
            num_paths = sum(
                [src_ancestors[topic] * tgt_children[topic] for topic in bridge_topics]
            )
            return (deg_sep, num_paths, None)

        # Work backwards from bridge topics to source.
        # We keep track of paths by bridge node so we can do more efficient
        # cross-product.
        src_to_bridge_paths = defaultdict(list)
        frontier = deque([[bridge_topic] for bridge_topic in bridge_topics])
        while frontier:
            path = frontier.popleft()
            ancestors = src_ancestors[path[0]]
            for ancestor in ancestors:
                if ancestor == src_idx:
                    path = [index_topic_map[ancestor]] + [
                        index_topic_map[x] for x in path
                    ]
                    src_to_bridge_paths[path[-1]].append(path)
                else:
                    frontier.append([ancestor] + path)

        # Work forward from bridge topics to target.
        # We keep track of paths by bridge node so we can do more efficient
        # cross-product.
        bridge_to_tgt_paths = defaultdict(list)
        frontier = deque([[bridge_topic] for bridge_topic in bridge_topics])
        while frontier:
            path = frontier.popleft()
            children = tgt_children[path[-1]]
            for child in children:
                if child == tgt_idx:
                    path = [index_topic_map[x] for x in path] + [index_topic_map[child]]
                    bridge_to_tgt_paths[path[0]].append(path)
                else:
                    frontier.append(path + [child])

        bridge_topics = [index_topic_map[topic] for topic in bridge_topics]

        # Cross-join source-to-bridge with bridge-to-target
        paths = [
            # Make sure to not duplicate the bridge topics.
            src_to_bridge_path + bridge_to_tgt_path[1:]
            for topic in bridge_topics
            for src_to_bridge_path in src_to_bridge_paths[topic]
            for bridge_to_tgt_path in bridge_to_tgt_paths[topic]
        ]

        return (deg_sep, len(paths), sorted(paths))

    def get_children(self, topic: str, directed: bool = True) -> Set[str]:
        """Get child topics of the given topic.

        Args:
            topic: A valid wikipedia topic.
            directed: Whether to use directed or undirected connections.
                Note that for undirected the result will be exactly the
                same as `get_ancestors`.

        Returns:
            Set of child topics.
        """
        topic = self.get_standard(topic)
        index_topic_map = self.index_topic_map
        return {
            index_topic_map[idx]
            for idx in self._get_children(self.topic_index_map[topic], directed)
        }

    def get_ancestors(self, topic: str, directed: bool = True) -> Set[str]:
        """Get ancestor topics of the given topic.

        Args:
            topic: A valid wikipedia topic.
            directed: Whether to use directed or undirected connections.
                Note that for undirected the result will be exactly the
                same as `get_children`.

        Returns:
            Set of ancestor topics.
        """
        topic = self.get_standard(topic)
        index_topic_map = self.index_topic_map
        return {
            index_topic_map[idx]
            for idx in self._get_ancestors(self.topic_index_map[topic], directed)
        }

    def _get_children(self, topic: int, directed: bool = True) -> Set[int]:
        if directed:
            res = self._get_directed_children(topic)
        else:
            res = self._get_undirected_neighbors(topic)
        return res

    def _get_ancestors(self, topic: int, directed: bool = True) -> Set[int]:
        if directed:
            res = self._get_directed_ancestors(topic)
        else:
            res = self._get_undirected_neighbors(topic)
        return res

    def _get_undirected_neighbors(self, topic: int) -> Set[int]:
        if self._optimize_memory:
            res = self._get_directed_children(topic) | self._get_directed_ancestors(
                topic
            )
        else:
            adj_mat_csr = self.adj_matrix_undirected_csr
            res = set(
                adj_mat_csr.indices[
                    adj_mat_csr.indptr[topic] : adj_mat_csr.indptr[topic + 1]
                ]
            )
        return res

    def _get_directed_children(self, topic: int) -> Set[int]:
        adj_mat_csr = self.adj_matrix_directed_csr
        return set(
            adj_mat_csr.indices[
                adj_mat_csr.indptr[topic] : adj_mat_csr.indptr[topic + 1]
            ]
        )

    def _get_directed_ancestors(self, topic: int) -> Set[int]:
        adj_mat_csc = self.adj_matrix_directed_csc
        return set(
            adj_mat_csc.indices[
                adj_mat_csc.indptr[topic] : adj_mat_csc.indptr[topic + 1]
            ]
        )

    def __str__(self):
        num_topics = len(self._topic_index_map) if self._topic_index_map else None
        return (
            f"WikiGraph(num_topics={num_topics or '<uninitialized>'}"
            f", optimize_memory={self._optimize_memory})"
        )

    __repr__ = __str__
