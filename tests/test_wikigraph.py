import pytest

from pywikigraph import WikiGraph

#                             +---+
#                 +---------->| C |---+
#                 |           +---+   +--->+---+        +---+
#               +---+                      | F -------->| H |+-----+
#      +------->| A |                  +-->+---+   +----+---+      |
#      |        +---+                  |           |               |
#      |          |                    |      +----+               |
#      |          |                    |      |                    |
#    +---+        +---------->+---+    |      |         +---+      +-->+---+
#    | S |                    | D |----+      |     +-->| I |--------->| T |
#    +---+        +---------->+---+           |     |   +---+      +-->+---+
#      |          |                           v     |              |
#      |          |                         +-+-+   |              |
#      |        +---+         +---+   +---->| G |---+              |
#      +------->| B |+------->| E |---+     +---+                  |
#               +---+         +---+           |         +---+      |
#                                             +-------->| J |------+
#                                                       +---+
DEMO_GRAPH_NODE_CHILDREN = [
    ("S", ["A", "B"]),
    ("A", ["C", "D"]),
    ("B", ["D", "E"]),
    ("C", ["F"]),
    ("D", ["F"]),
    ("E", ["G"]),
    ("F", ["H"]),
    ("G", ["I", "J"]),
    ("H", ["G", "T"]),
    ("I", ["T"]),
    ("J", ["T"]),
]

DIRECTED_TEST_CASES = [
    ("G", "H", []),
    ("H", "G", [["h", "g"]]),
    (
        "S",
        "T",
        [
            ["s", "a", "c", "f", "h", "t"],
            ["s", "a", "d", "f", "h", "t"],
            ["s", "b", "d", "f", "h", "t"],
            ["s", "b", "e", "g", "i", "t"],
            ["s", "b", "e", "g", "j", "t"],
        ],
    ),
]

UNDIRECTED_TEST_CASES = [
    ("G", "H", [["g", "h"]]),
    ("H", "G", [["h", "g"]]),
    (
        "S",
        "T",
        [
            ["s", "a", "c", "f", "h", "t"],
            ["s", "a", "d", "f", "h", "t"],
            ["s", "b", "d", "f", "h", "t"],
            ["s", "b", "e", "g", "h", "t"],
            ["s", "b", "e", "g", "i", "t"],
            ["s", "b", "e", "g", "j", "t"],
        ],
    ),
]


@pytest.fixture
def demo_wikigraph_nm():
    wg = WikiGraph(optimize_memory=False)
    wg.set_graph(DEMO_GRAPH_NODE_CHILDREN)
    return wg


@pytest.fixture
def demo_wikigraph():
    wg = WikiGraph()
    wg.set_graph(DEMO_GRAPH_NODE_CHILDREN)
    return wg


def get_paths_info_from_paths(paths, no_paths=False):
    if not paths:
        return (-1, 0, None if no_paths else paths)
    return (len(paths[0]) - 1, len(paths), None if no_paths else paths)


def assert_paths_infos_equal(paths_info_1, paths_info_2):
    assert paths_info_1[0] == paths_info_2[0]
    assert paths_info_1[1] == paths_info_2[1]
    if paths_info_1[2] is None:
        assert paths_info_2[2] is None
    else:
        assert sorted(paths_info_1[2]) == sorted(paths_info_2[2])


def test_shortest_path_same_node(demo_wikigraph):
    for topic in demo_wikigraph.topic_index_map:
        topic = demo_wikigraph.get_standard(topic)
        paths_info = demo_wikigraph.get_shortest_paths_info(topic, topic)
        assert paths_info == get_paths_info_from_paths([[topic]])


def test_shortest_paths_directed(demo_wikigraph, demo_wikigraph_nm):
    for src, tgt, expected_paths in DIRECTED_TEST_CASES:
        for no_paths in [True, False]:
            expected_paths_info = get_paths_info_from_paths(
                expected_paths, no_paths=no_paths
            )
            for wg in [demo_wikigraph, demo_wikigraph_nm]:
                paths_info = wg.get_shortest_paths_info(
                    src, tgt, directed=True, no_paths=no_paths
                )
                assert_paths_infos_equal(paths_info, expected_paths_info)


def test_shortest_paths_undirected(demo_wikigraph, demo_wikigraph_nm):
    for src, tgt, expected_paths in UNDIRECTED_TEST_CASES:
        for no_paths in [True, False]:
            expected_paths_info = get_paths_info_from_paths(
                expected_paths, no_paths=no_paths
            )
            for wg in [demo_wikigraph, demo_wikigraph_nm]:
                paths_info = wg.get_shortest_paths_info(
                    src, tgt, directed=False, no_paths=no_paths
                )
                assert_paths_infos_equal(paths_info, expected_paths_info)


def test_get_children(demo_wikigraph, demo_wikigraph_nm):
    for wg in [demo_wikigraph, demo_wikigraph_nm]:
        assert wg.get_children("S") == set(["a", "b"])
        assert wg.get_children("T") == set([])


def test_get_ancestors(demo_wikigraph, demo_wikigraph_nm):
    for wg in [demo_wikigraph, demo_wikigraph_nm]:
        assert wg.get_ancestors("T") == set(["h", "i", "j"])
        assert wg.get_ancestors("S") == set([])
