from itertools import chain
from typing import Optional, Tuple

from py2neo.data import PropertyDict


class GraphBase:
    pass


class Subgraph(GraphBase):
    """A :class:`Subgraph` is an arbitrary collection of :class:`.Node`s
    and :class:`.Relationship`s between them stored in an adjacency list representation,
    optimized for use in `alchemiscale`.

    .. describe:: subgraph | other | ...

        Union.
        Return a new subgraph containing all nodes and relationships from *subgraph* as well as all those from *other*.
        Any entities common to both will only be included once.

    .. describe:: subgraph & other & ...

        Intersection.
        Return a new subgraph containing all nodes and relationships common to both *subgraph* and *other*.

    .. describe:: subgraph - other - ...

        Difference.
        Return a new subgraph containing all nodes and relationships that exist in *subgraph* but do not exist in *other*,
        as well as all nodes that are connected by the relationships in *subgraph* regardless of whether or not they exist in *other*.

    .. describe:: subgraph ^ other ^ ...

        Symmetric difference.
        Return a new subgraph containing all nodes and relationships that exist in *subgraph* or *other*, but not in both,
        as well as all nodes that are connected by those relationships regardless of whether or not they are common to *subgraph* and *other*.
    """


class Node(PropertyDict):

    # Next edge in outgoing and incoming adjacency lists
    _next: Tuple
    
    def __init__(self, *labels, **properties):
        self._labels = set(labels)
        PropertyDict.__init__(self, properties)
