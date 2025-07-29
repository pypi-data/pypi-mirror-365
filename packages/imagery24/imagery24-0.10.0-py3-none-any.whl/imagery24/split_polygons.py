from __future__ import annotations

import logging
from typing import List, Tuple

import networkx as nx
from centerline.geometry import Centerline
from shapely import line_merge, simplify, voronoi_polygons
from shapely.geometry import (
    LineString,
    MultiLineString,
    MultiPoint,
    Point,
    Polygon,
)
from shapely.ops import linemerge

__all__ = ["split_polygon"]

TOLERANCE: float = 1e-8  # snap grid size when deduplicating vertices


Coordinate = tuple[float, float]

# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------


def _lines_to_graph(lines: list[LineString]) -> nx.Graph:
    """Convert *lines* to an undirected NetworkX graph.

    For each *LineString* only its first & last coordinate are kept as nodes;
    one edge connects them and stores:
    * ``length`` – full geometric length (``line.length``)
    * ``geom``   – the original *LineString* object
    """
    G: nx.Graph = nx.Graph()

    for line in lines:
        start, end = line.coords[0], line.coords[-1]
        G.add_node(start, pos=start)
        G.add_node(end, pos=end)
        if not G.has_edge(start, end):
            G.add_edge(start, end, length=line.length, geom=line)

    return G


def _initial_short_leaves(G: nx.Graph, threshold: float) -> List[Coordinate]:
    leaves: List[Coordinate] = []
    for n in G.nodes:
        if G.degree[n] == 1:
            neighbor = next(iter(G.neighbors(n)))
            if G.edges[n, neighbor]["length"] < threshold:
                leaves.append(n)
    return leaves


def _prune_short_leaves(
    G: nx.Graph, min_length: float, *, inplace: bool = False
) -> nx.Graph:
    """Remove degree‑1 nodes whose edge length < ``min_length`` (iterative)."""
    if min_length < 0:
        raise ValueError("min_length must be non‑negative")

    H = G if inplace else G.copy()
    queue = _initial_short_leaves(H, min_length)

    while queue:
        leaf = queue.pop()
        if leaf not in H or H.degree[leaf] != 1:
            continue
        nbr = next(iter(H.neighbors(leaf)))
        if H.edges[leaf, nbr]["length"] >= min_length:
            continue
        H.remove_node(leaf)
        if H.degree[nbr] == 1:
            nbr2 = next(iter(H.neighbors(nbr)))
            if H.edges[nbr, nbr2]["length"] < min_length:
                queue.append(nbr)
    return H


def _graph_diameter_path(G: nx.Graph) -> List[Coordinate]:
    if G.number_of_nodes() <= 1:
        return list(G.nodes)
    lengths = nx.all_pairs_dijkstra_path_length(G, weight="length")
    u_max: Coordinate | None = None
    v_max: Coordinate | None = None
    max_dist = -1.0
    for u, dist_map in lengths:
        for v, dist in dist_map.items():
            if dist > max_dist:
                u_max, v_max, max_dist = u, v, dist
    if u_max is None or v_max is None:
        return []
    return nx.shortest_path(G, u_max, v_max, weight="length")


def enumerate_graph_longest_path(
    G: nx.Graph,
) -> Tuple[List[Coordinate], List[Tuple[Coordinate, Coordinate]]]:
    if G.number_of_nodes() == 0:
        return [], []
    path = _graph_diameter_path(G)
    node_order = path + [n for n in G.nodes if n not in path]
    for idx, n in enumerate(node_order):
        G.nodes[n]["id"] = idx
    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    remaining_edges = [e for e in G.edges if set(e) not in map(set, path_edges)]
    edge_order = path_edges + remaining_edges
    for idx, (u, v) in enumerate(edge_order):
        if G.has_edge(u, v):
            G.edges[u, v]["id"] = idx
        else:
            G.edges[v, u]["id"] = idx
    return node_order, edge_order


def _process_lines(
    lines: list[LineString], *, min_leaf_length: float = 0.0
) -> List[LineString]:
    """Run the full pipeline and return **ordered, oriented** LineStrings.

    Parameters
    ----------
    geometry : LineString | MultiLineString
    min_leaf_length : float, optional
        Leaves shorter than this are pruned (default 0 = keep all).

    Returns
    -------
    list[LineString]
        Ordered so that each line starts at the node with the smaller ``id`` and
        ends at the node with the larger ``id``; list itself sorted by that
        start‑node id.
    """
    # 1‑2. Build graph
    G = _lines_to_graph(lines)

    # 3. Prune short leaves
    G = _prune_short_leaves(G, min_leaf_length)

    # 4. Gather remaining lines & linemerge
    remaining_lines = [d["geom"] for *_, d in G.edges(data=True)]
    merged = linemerge(remaining_lines)
    if isinstance(merged, LineString):
        merged_lines: List[LineString] = [merged]
    else:
        merged_lines = list(merged.geoms)

    # 5. Enumerate graph
    enumerate_graph_longest_path(G)

    # 6. Orient & order lines
    oriented: List[Tuple[int, LineString]] = []
    for line in merged_lines:
        start, end = line.coords[0], line.coords[-1]
        id_start = G.nodes[start]["id"]
        id_end = G.nodes[end]["id"]
        if id_start > id_end:
            line = LineString(list(reversed(line.coords)))
            id_start, id_end = id_end, id_start
        oriented.append((id_end, line))
    oriented.sort(key=lambda tpl: tpl[0])  # sort by start id
    return [ln for _, ln in oriented]


def line_list(geometry: LineString | MultiLineString) -> list[LineString]:
    return list(geometry.geoms) if isinstance(geometry, MultiLineString) else [geometry]


def _round_pt(x: float, y: float, tolerance: float = TOLERANCE) -> Tuple[float, float]:
    """Snap *x*, *y* to a *tolerance*‑sized grid so nearly‑identical vertices collapse."""
    return (round(x / tolerance) * tolerance, round(y / tolerance) * tolerance)


def _prune_adjacent_leaves(
    graph: nx.Graph, spacing: float, weight: str = "weight"
) -> None:
    """
    For every non‑leaf node, keep only the incident leaf whose edge has
    the highest *weight* attribute; drop the other leaves (and their edges).

    Modifies G in place and also returns it for convenience.

    Parameters
    ----------
    G : networkx.Graph
        Undirected graph with edge attribute *weight*.
    weight : str
        Name of the edge‑weight attribute (default: "weight").
    """
    to_remove = []

    for parent in graph.nodes:
        # leaves directly connected to *parent*
        leaves = [
            nbr
            for nbr in graph.neighbors(parent)
            if graph.degree[nbr] == 1 and graph[parent][nbr].get(weight, 0) < spacing
        ]

        # print([G[parent][leaf].get(weight, 0) for leaf in leaves])
        if len(leaves) <= 1:
            continue  # nothing to prune here

        # pick the best leaf (highest‑weight edge)
        best = max(leaves, key=lambda leaf: graph[parent][leaf].get(weight, 0))

        # schedule all other leaves for removal
        to_remove.extend(leaf for leaf in leaves if leaf != best)
        # print("to remove:", to_remove)

    graph.remove_nodes_from(to_remove)


def _extract_centerline(polygon: Polygon, spacing: float) -> list[LineString]:
    """Return a de‑branched centreline for *polygon*.

    The heavy‑lifting is done by *Centerline* from the ``centerline`` package, but the
    raw result is *cleaned* by merging contiguous segments and pruning minor twigs so
    that downstream point‑generation behaves predictably.
    """
    cl_raw = line_merge(Centerline(polygon, spacing / 4).geometry)
    lines = line_list(cl_raw)
    G = nx.Graph()

    for idx, ln in enumerate(lines):
        start = _round_pt(*ln.coords[0])
        end = _round_pt(*ln.coords[-1])
        G.add_edge(start, end, weight=ln.length, idx=idx)

    _prune_adjacent_leaves(G, spacing)

    indexes = set(d["idx"] for u, v, d in G.edges(data=True))

    non_leaves = []

    for idx, line in enumerate(lines):
        if idx in indexes:
            non_leaves.append(line)
    simplified = simplify(linemerge(non_leaves), spacing / 10)

    return line_list(linemerge([x for x in line_list(simplified)]))


def _spaced_points(lines: list[LineString], spacing: float) -> List[Point]:
    """Return approximately equally‑spaced points *on every branch* of *lines*.

    * ``spacing`` refers to the *desired* interval. Because the total branch length is
      finite, the exact distance between adjacent points is *adjusted* (up to ±½ spacing)
      so that the points are perfectly evenly distributed along each branch.
    * No point is placed **exactly** at a junction or branch‑start – the first point is
      offset by ½ adjusted spacing to avoid duplicates between branches.
    """
    if spacing <= 0:
        raise ValueError("spacing must be > 0")

    placed: list[Point] = []

    for line in lines:
        length = line.length
        if length < spacing:
            continue  # too short for even one point

        n = int((length - spacing) // spacing) + 1
        adjusted_spacing = length / n

        for k in range(0, n):
            pt = line.interpolate((k + 0.5) * adjusted_spacing)
            placed.append(pt)

    return placed


def _voronoi_split(poly: Polygon, seeds: List[Point]) -> List[Polygon]:
    """Return a list of polygons obtained by clipping the Voronoi diagram of *seeds*
    with *poly*.

    Multi‑polygons are post‑processed so that the largest component stays in the
    resulting list while every smaller component is merged into the *smallest*
    of its neighbouring polygons.  The original order (driven by the Voronoi
    cells) is preserved.
    """

    # 1. Build the (ordered) Voronoi diagram clipped to *poly*
    diagram = voronoi_polygons(MultiPoint(seeds), extend_to=poly, ordered=True)

    polys: List[Polygon] = []  # final output (in order)
    pending_smalls: list[Polygon] = []  # smaller pieces waiting to be merged

    # 2. Collect polygons, keeping only the biggest piece of every MultiPolygon
    for cell in diagram.geoms:
        clipped = cell.intersection(poly)
        if clipped.is_empty:
            continue

        if isinstance(clipped, Polygon):
            polys.append(clipped)
        else:  # MultiPolygon
            parts = sorted(clipped.geoms, key=lambda g: g.area, reverse=True)
            polys.append(parts[0])  # keep the biggest piece in place
            pending_smalls.extend(parts[1:])  # queue all the rest for merging

    # 3. Merge each small piece with the *smallest* of its neighbours
    for small in pending_smalls:
        # Find neighbours that touch or intersect the small piece
        neighbour_ids = [
            i for i, p in enumerate(polys) if p.touches(small) or p.intersects(small)
        ]

        if not neighbour_ids:  # fallback: pick the overall smallest polygon
            neighbour_ids = range(len(polys))

        # Choose the neighbour with the smallest area among the candidates
        target_idx = min(neighbour_ids, key=lambda i: polys[i].area)

        # Union the small piece into the chosen neighbour
        polys[target_idx] = polys[target_idx].union(small)

    return polys


def split_polygon(polygon: Polygon, spacing: float = 5.0) -> list[Polygon]:
    """Split *polygon* into Voronoi cells derived from an approximated centreline.

    Parameters
    ----------
    polygon
        The input geometry to split. Must be a valid, *single* ``Polygon`` (holes are OK).
    spacing
        Approximate distance between consecutive seed points along the centreline.

    Returns
    -------
    MultiPolygon
        A collection of sub‑polygons whose union equals (or is very close to)
        the original *polygon*.

    Notes
    -----
    * A smaller ``spacing`` yields more seed points and therefore more resulting
      polygons at the expense of increased run time.
    * Because of floating‑point arithmetic and the nature of the Voronoi algorithm,
      the union of the returned cells may be *slightly* smaller than the original
      geometry. Buffering the input by a *tiny* amount (~1e‑8) beforehand can help
      if strict area preservation is important.
    """

    try:
        centreline = _extract_centerline(polygon, spacing)
        ordered_lines = _process_lines(centreline, min_leaf_length=100)
        seeds = _spaced_points(ordered_lines, spacing)
        result = _voronoi_split(polygon, seeds)
        logging.info(f"Split polygon into {len(result)} cells with spacing {spacing}")
        return result
    except Exception:
        # Provide context and re‑raise – calers can catch the same *exc*
        raise
