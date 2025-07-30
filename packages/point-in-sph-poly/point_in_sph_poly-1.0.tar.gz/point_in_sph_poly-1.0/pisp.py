"""
Single-file Python package containing a reimplementation of
[sphericalpolygon](https://github.com/ryanketzner/sphericalpolygon).
"""

# standard imports
from __future__ import annotations
from time import perf_counter
import numpy as np
from numba import njit, prange
from numpy.typing import NDArray
from numba.typed import List


# part 1: Pyhton class that provides (pre)processing functionality


class SphericalPolygon:
    """
    Class representing a polygon defined on a unit sphere, with methods
    to check whether given points are inside or outside of it.
    """

    vertices_Qia: NDArray[np.floating]
    """
    Vertices of the polygon in the query frame as ``(2, m+1)``
    inclination/azimuth pairs [rad]
    """
    poles_Qxyz: NDArray[np.floating]
    """
    Poles of the edges in the query frame as ``(m, 3)``
    cartesian coordinates [-]
    """
    R_I2Q: NDArray[np.floating]
    """
    3D rotation matrix from the primary to the query cartesian frame [-]
    """
    lunes_az: NDArray[np.floating] | None = None
    """
    When preprocessing is active: azimuth coordinates of shape ``(m+1, )`` [rad]
    of lune boundaries
    """
    tree: List[NDArray[np.unsignedinteger]] | None = None
    """
    When preprocessing is active: list of arrays of edge indices to consider when
    checking whether a query point is inside the polygon or not (length ``m+1``)
    """
    timeit: bool = False
    """
    If set, time and print the (pre)processing runtimes.
    """

    @property
    def num_edges(self):
        """Number of edges in polygon [-]"""
        return self.poles_Qxyz.shape[0]

    def __init__(
        self,
        vertices_Qia: NDArray[np.floating],
        poles_Qxyz: NDArray[np.floating],
        R_I2Q: NDArray[np.floating],
    ):
        """
        Base constructor for spherical polygon from vertices already in the
        appropriate format.

        Parameters
        ----------
        vertices_Qia
            Vertices of the polygon in the query frame as ``(2, m+1)``
            contiguous inclination/azimuth pairs [rad]
        poles_Qxyz
            Poles of the edges in the query frame as ``(m, 2)``
            contiguous cartesian coordinates [-]
        R_I2Q
            3D rotation matrix from the primary to the query cartesian frame [-]
        """
        # check shapes
        assert vertices_Qia.ndim == poles_Qxyz.ndim == 2
        assert vertices_Qia.shape[1] == poles_Qxyz.shape[0] + 1
        assert vertices_Qia.shape[0] == 2
        assert poles_Qxyz.shape[1] == 3
        assert R_I2Q.shape == (3, 3)
        # check contiguity
        assert vertices_Qia.flags.c_contiguous
        assert poles_Qxyz.flags.c_contiguous
        # save
        self.vertices_Qia = vertices_Qia
        self.poles_Qxyz = poles_Qxyz
        self.R_I2Q = R_I2Q
        # done

    @classmethod
    def from_inc_az(
        cls,
        vertices_Iia: NDArray[np.floating],
        inside_Iia: NDArray[np.floating] | None = None,
    ) -> SphericalPolygon:
        """
        Construct a spherical polygon from global (initial) inclination/azimuth
        coordinates.
        If no inside point is given, it is assumed that the last vertex is not
        a vertex point but the inside point instead.

        Parameters
        ----------
        vertices_Iia
            Vertices of the polygon in the initial (global) frame as ``(m+1, 2)``
            inclination/azimuth pairs [rad]
        inside_Iia
            Vertex coordinate of the inside point in the initial (global) frame
            as a single inclination/azimuth pair [rad]
        """
        # extract inside point if necessary
        if inside_Iia is None:
            inside_Iia = vertices_Iia[-1, :]
            vertices_Iia = vertices_Iia[:-1, :]
        # rotate to initial cartesian frame I
        vertices_Ixyz = spherical2cartesian(vertices_Iia)
        inside_Ixyz = spherical2cartesian(inside_Iia[None, :])
        # define query frame Q based on inside point
        zhat_Q = inside_Ixyz[0, :]
        yhat_Q = np.cross(zhat_Q, vertices_Ixyz[0, :])
        xhat_Q = np.cross(yhat_Q, zhat_Q)
        R_I2Q = np.stack([xhat_Q, yhat_Q, zhat_Q], axis=0)
        # rotate points to query frame
        vertices_Qxyz = (R_I2Q @ vertices_Ixyz.T).T
        # inside_Qxyz is just [0, 0, 1] now by construction
        # compute poles in query frame
        poles_Qxyz = np.cross(
            vertices_Qxyz[:-1, :], vertices_Qxyz[1:, :], axisa=1, axisb=1
        )
        # convert query frame cartesian coordinates to spherical inclination and azimuth
        vertices_Qia = cartesian2spherical(vertices_Qxyz)
        vertices_Qia[vertices_Qia[:, 1] < 0, 1] += 2 * np.pi
        # transpose and make contiguous
        vertices_Qia = np.ascontiguousarray(vertices_Qia.T)
        # instantiate class
        return cls(vertices_Qia, poles_Qxyz, R_I2Q)

    @classmethod
    def from_lon_lat(
        cls,
        vertices_lon_lat: NDArray[np.floating],
        inside_lon_lat: NDArray[np.floating] | None = None,
    ) -> SphericalPolygon:
        """
        Thin wrapper around `SphericalPolygon.from_inc_az`, accepting
        geographic longitude/latitude pairs as input instead.
        """
        # convert
        vertices_Iia = lola2incaz(vertices_lon_lat)
        inside_Iia = None if inside_lon_lat is None else lola2incaz(inside_lon_lat)[0]
        # continue instantiating
        return SphericalPolygon.from_inc_az(vertices_Iia, inside_Iia)

    def preprocess(self):
        """
        Build the lunes and tree index to speed up later checks.

        Calls `slice_array_preprocess`.
        """
        # build sorted vertex azimuths and lunes
        vertices_az = self.vertices_Qia[1, :]
        vertices_az_sorted = np.sort(
            np.stack([vertices_az[:-1], vertices_az[1:]], axis=1), axis=1
        )
        self.lunes_az = np.r_[np.unique(vertices_az), 2 * np.pi]
        # initialize output
        self.tree = List(np.array([], dtype=np.uint) for _ in range(self.num_edges))
        # run preprocessing on tree
        if self.timeit:
            runtime = -perf_counter()
        slice_array_preprocess(
            self.tree,
            np.arange(self.num_edges, dtype=np.uint),
            vertices_az_sorted,
            self.lunes_az,
            0,
            self.num_edges,
        )
        if self.timeit:
            runtime += perf_counter()
            print(
                f"Preprocessing took {runtime*1e6:.1f} µs "
                f"({runtime*1e6/self.num_edges:.1f} µs per edge)"
            )
        # done

    def contains(
        self, queries_Qia: NDArray[np.floating], queries_Qxyz: NDArray[np.floating]
    ) -> NDArray[np.int8]:
        """
        Low-level implementation of containment check with inputs already
        in the appropriate format.
        If the `SphericalPolygon` was preprocessed, it calls
        `tree_edges_contain_queries`, else `edges_contain_queries`.

        Parameters
        ----------
        queries_Qia
            Query points in the query frame as ``(2, n)``
            contiguous inclination/azimuth pairs [rad]
        queries_Qxyz
            Query points in the query frame as ``(n, 3)``
            contiguous cartesian coordinates [-]

        Returns
        -------
        q_contained
            Array indicating whether each query point is contained (``1``),
            not contained (``0``), or on an edge (``-1``).
        """
        # check shapes
        assert queries_Qia.shape[1] == queries_Qxyz.shape[0]
        assert queries_Qia.shape[0] == 2
        assert queries_Qxyz.shape[1] == 3
        # check contiguity
        assert queries_Qia.flags.c_contiguous
        assert queries_Qxyz.flags.c_contiguous
        # run check
        if (self.lunes_az is None) or (self.tree is None):
            if self.timeit:
                runtime = -perf_counter()
            q_contained = edges_contain_queries(
                self.vertices_Qia[1, :],
                self.vertices_Qia[0, :],
                queries_Qia[1, :],
                queries_Qia[0, :],
                self.poles_Qxyz,
                queries_Qxyz,
            )
            if self.timeit:
                runtime += perf_counter()
                print(
                    f"Processing (w/o preprocessing) took {runtime*1e6:.1f} µs "
                    f"({runtime*1e6/queries_Qxyz.shape[0]:.1f} µs per point)"
                )
        else:
            if self.timeit:
                runtime = -perf_counter()
            q_contained = tree_edges_contain_queries(
                self.vertices_Qia[1, :],
                self.vertices_Qia[0, :],
                queries_Qia[1, :],
                queries_Qia[0, :],
                self.poles_Qxyz,
                queries_Qxyz,
                self.lunes_az,
                self.tree,
            )
            if self.timeit:
                runtime += perf_counter()
                print(
                    f"Processing (w/ preprocessing) took {runtime*1e6:.1f} µs "
                    f"({runtime*1e6/queries_Qxyz.shape[0]:.1f} µs per point)"
                )
        # done
        return q_contained

    def contains_inc_az(self, queries_Iia: NDArray[np.floating]) -> NDArray[np.int8]:
        """
        Check whether a set of inclination/azimuth coordinates
        in the initial spherical frame are contained within
        Will use the preprocessed tree, if available.

        Parameters
        ----------
        queries_Qia
            Query points in the query frame as ``(n, 2)``
            inclination/azimuth pairs [rad]

        Returns
        -------
        q_contained
            Array indicating whether each query point is contained (``1``),
            not contained (``0``), or on an edge (``-1``).
        """
        # rotate to initial cartesian frame
        queries_Ixyz = spherical2cartesian(queries_Iia)
        # rotate to query cartesian frame
        queries_Qxyz = np.ascontiguousarray((self.R_I2Q @ queries_Ixyz.T).T)
        # convert to query spherical frame
        queries_Qia = cartesian2spherical(queries_Qxyz)
        queries_Qia[queries_Qia[:, 1] < 0, 1] += 2 * np.pi
        # transpose and make contiguous
        queries_Qia = np.ascontiguousarray(queries_Qia.T)
        # perform check
        return self.contains(queries_Qia, queries_Qxyz)

    def contains_lola(self, queries_Ilola: NDArray[np.floating]) -> NDArray[np.int8]:
        """
        Check whether a set of longitude/latitude coordinates
        in the initial spherical frame are contained within
        Will use the preprocessed tree, if available.

        Thin wrapper around `SphericalPolygon.contains_inc_az`

        Parameters
        ----------
        queries_Qia
            Query points in the query frame as ``(n, 2)``
            longitude/latitude pairs [rad]

        Returns
        -------
        q_contained
            Array indicating whether each query point is contained (``1``),
            not contained (``0``), or on an edge (``-1``).
        """
        # convert
        queries_Iia = lola2incaz(queries_Ilola)
        # continue check
        return self.contains_inc_az(queries_Iia)


# part 2: numba-optimized functions from sphericalpolygon C++-code


@njit(cache=True)
def is_inc_bounded(bound1: float, bound2: float, inc: float) -> np.int8:
    """
    Reimplementation of `util::latBounded`.

    Checks whether an inclination is bounded by the minor arc
    defined by two other inclinations.

    Parameters
    ----------
    bound1
        First inclination [rad]
    bound2
        Second inclination [rad]
    inc
        Inclination to check [rad]

    Returns
    -------
    containcode
        ``-1`` if on the edge,
        ``2`` if it passes the edge,
        or ``-2`` if it doesn't pass the edge
    """
    if bound2 > bound1:
        if (inc >= bound1) and (inc <= bound2):
            return -1
        elif inc > bound2:
            return 2
        else:
            return -2
    else:
        if (inc >= bound2) and (inc <= bound1):
            return -1
        elif inc > bound1:
            return 2
        else:
            return -2


@njit(cache=True)
def is_az_bounded(bound1: float, bound2: float, az: float) -> bool:
    """
    Reimplementation of `util::lonBounded`.

    Checks whether an azimuth is bounded by the minor arc
    defined by two other azimuths.

    Parameters
    ----------
    bound1
        First azimuth [rad]
    bound2
        Second azimuth [rad]
    inc
        Azimuth to check [rad]

    Returns
    -------
    bounded
        ``True`` if bounded, ``False`` if not
    """
    bounded = (az >= bound1) and (az <= bound2)
    if (bound2 - bound1) < np.pi:
        return bounded
    else:
        return not bounded


@njit(cache=True)
def edge_bounds_point(
    az1: float, az2: float, inc1: float, inc2: float, az: float, inc: float
) -> np.int8:
    """
    Reimplementation of `Edge::boundsPoint`.

    Checks the condition of necessary strike.

    Calls `is_inc_bounded` and `is_az_bounded`.

    Parameters
    ----------
    az1
        Azimuth of first vertex [rad]
    az2
        Azimuth of second vertex [rad]
    inc1
        Inclination of first vertex [rad]
    inc2
        Inclination of second vertex [rad]
    az
        Azimuth of vertex to check [rad]
    inc
        Inclination of vertex to check [rad]

    Returns
    -------
    containcode
        Result if the condition of necessary strike: if all azimuths
        are equal, the result of `is_inc_bounded`, if the azimuth is not
        equal to one of the bounding azimuths, then the result of
        `is_az_bounded`, else whether the azimuth is equal to one of
        the bounding azimuths
    """
    # get bounding azimuths in increasing order
    if az1 < az2:
        bound1 = az1
        bound2 = az2
    else:
        bound1 = az2
        bound2 = az1
    # check condition
    if (az == bound1) or (az == bound2):
        if (az == bound1) and (az == bound2):
            return is_inc_bounded(inc1, inc2, inc)
        elif (bound2 - bound1) < np.pi:
            return np.int8(az == bound2)
        else:
            return np.int8(az == bound1)
    else:
        return np.int8(is_az_bounded(bound1, bound2, az))


@njit(cache=True)
def edge_crosses_boundary(
    pole: NDArray[np.floating], inside_dot_pole: float, query: NDArray[np.floating]
) -> np.int8:
    """
    Reimplementation of `Edge::crossesBoundary`.

    Performs the hemisphere check.

    Parameters
    ----------
    pole
        Pole of the edge to check cartesian coordinates [-]
    inside_dot_pole
        Dot product of inside point with pole in query frame [-]
    query
        Point to check in query frame [-]

    Returns
    -------
    containcode
        ``-1`` if the query point is directly on the edge,
        ``0`` if it is on the same side as the inside point, or
        ``1`` if it is on the opposide side as the inside point
    """
    query_dot_pole = np.dot(query, pole)
    if query_dot_pole == 0.0:
        return -1
    elif query_dot_pole * inside_dot_pole < 0.0:
        return 1
    else:
        return 0


@njit(cache=True)
def edge_contains(
    az1: float,
    az2: float,
    inc1: float,
    inc2: float,
    az: float,
    inc: float,
    pole: NDArray[np.floating],
    inside_dot_pole: float,
    query: NDArray[np.floating],
) -> np.int8:
    """
    Reimplements `Edge::contains`.

    Check whether a query point is inside of an edge of the polygon.

    Calls `edge_bounds_point` and `edge_crosses_boundary`.

    Parameters
    ----------
    az1
        Azimuth of first vertex [rad]
    az2
        Azimuth of second vertex [rad]
    inc1
        Inclination of first vertex [rad]
    inc2
        Inclination of second vertex [rad]
    az
        Azimuth of vertex to check [rad]
    inc
        Inclination of vertex to check [rad]
    pole
        Pole of the edge to check cartesian coordinates [-]
    inside_dot_pole
        Dot product of inside point with pole in query frame [-]
    query
        Point to check in query frame [-]

    Returns
    -------
    containcode
        ``-1`` if the query point is directly on the edge,
        ``0`` if the arc from inside to query point does not cross the edge, or
        ``1`` if it does cross the edge
    """
    bounds = edge_bounds_point(az1, az2, inc1, inc2, az, inc)
    if bounds == 1:
        return edge_crosses_boundary(pole, inside_dot_pole, query)
    elif bounds == 2:
        return 1
    elif bounds == -2:
        return 0
    elif bounds == -1:
        return -1
    else:
        return 0


@njit(cache=True)
def slice_array_contains(
    parent_indices: NDArray[np.unsignedinteger],
    bound1: np.uint,
    bound2: np.uint,
    edges_az_sorted: NDArray[np.floating],
) -> list[np.uint]:
    """ "
    Reimplementation of `SliceArray::contains`.

    Checks whether a set of edges is part of a lune (bounds-defined).

    Calls `is_az_bounded`.

    Parameters
    ----------
    parent_indices
        Array of edge indices to check whether they are contained in a lune
    bound1
        Lower azimuth bound of the lune [rad]
    bound2
        Upper azimuth bound of the lune [rad]
    edges_az_sorted
        Array with the sorted azimuths of all edges [rad]

    Returns
    -------
    child_indices
        Index list of all edges contained in the lune
    """
    child_indices = []
    for i in prange(len(parent_indices)):
        vertex1 = edges_az_sorted[parent_indices[i], 0]
        vertex2 = edges_az_sorted[parent_indices[i], 1]
        condition1_1 = (vertex1 >= bound1) and (vertex1 <= bound2)
        condition1_2 = (vertex2 >= bound1) and (vertex2 <= bound2)
        condition2_1 = is_az_bounded(vertex1, vertex2, bound1 % (2 * np.pi))
        condition2_2 = is_az_bounded(vertex1, vertex2, bound2 % (2 * np.pi))
        if condition1_1 or condition1_2 or condition2_1 or condition2_2:
            child_indices.append(parent_indices[i])
    return child_indices


@njit(cache=True)
def slice_array_classify_edges(
    parent_indices: NDArray[np.unsignedinteger],
    edges_az_sorted: NDArray[np.floating],
    lunes_az: NDArray[np.floating],
    start: np.uint,
    end: np.uint,
) -> NDArray[np.unsignedinteger]:
    """
    Reimplementation of `SliceArray::classifyEdges`.

    Checks whether a set of edges is part of a lune (index-defined).

    Calls `slice_array_contains`.

    Parameters
    ----------
    parent_indices
        Array of edge indices to check whether they are contained in a lune
    edges_az_sorted
        Array with the sorted azimuths of all edges [rad]
    lunes_az
        Array of lune azimuths [rad]
    start
        Lower azimuth index of the lune
    end
        Upper azimuth index of the lune

    Returns
    -------
    child_indices
        Index array of all edges contained in the lune
    """
    bound1 = lunes_az[start]
    bound2 = lunes_az[end]
    child_indices = slice_array_contains(
        parent_indices, bound1, bound2, edges_az_sorted
    )
    return np.asarray(child_indices, dtype=np.uint)


@njit(cache=True)
def slice_array_preprocess(
    tree: list[NDArray[np.unsignedinteger]],
    parent_indices: NDArray[np.unsignedinteger],
    edges_az_sorted: NDArray[np.floating],
    lunes_az: NDArray[np.floating],
    start: np.uint,
    end: np.uint,
):
    """
    Reimplementation of `SliceArray::preprocess`.

    Builds the tree of edge indices needing to be checked given some
    input query azimuths.

    Calls `slice_array_classify_edges` and itself.

    Parameters
    ----------
    tree
        In- and output variable that contains the tree
    parent_indices
        Array of edge indices to check whether they are contained in a lune
    edges_az_sorted
        Array with the sorted azimuths of all edges [rad]
    lunes_az
        Array of lune azimuths [rad]
    start
        Lower azimuth index of the lune
    end
        Upper azimuth index of the lune
    """
    # get indices which still need to be considered
    child_indices = slice_array_classify_edges(
        parent_indices, edges_az_sorted, lunes_az, start, end
    )
    # found a leaf
    if end - start == 1:
        tree[start] = child_indices
        return
    # recursively build sub-tree
    else:
        mid = start + (end - start) // 2
        slice_array_preprocess(
            tree,
            child_indices,
            edges_az_sorted,
            lunes_az,
            start,
            mid,
        )
        slice_array_preprocess(
            tree,
            child_indices,
            edges_az_sorted,
            lunes_az,
            mid,
            end,
        )
    # done


@njit(cache=True)
def slice_array_get_tree_index(
    query_az: float, lunes_az: NDArray[np.floating]
) -> np.uint:
    """
    (Slightly modified) reimplementation of `SliceArray::getEdges`.

    Given a query azimuth, returns the tree index which contains
    the edges to consider.

    Parameters
    ----------
    query_az
        Query azimuth [rad]
    lunes_az
        Array of lune azimuths [rad]

    Returns
    -------
    start
        Tree index
    """
    start = 0
    end = lunes_az.size - 1
    while (end - start) > 1:
        mid = start + (end - start) // 2
        midaz = lunes_az[mid]
        if query_az <= midaz:
            end = mid
        else:
            start = mid
    return start


@njit(cache=True)
def edges_contain_queries(
    vertices_az: NDArray[np.floating],
    vertices_inc: NDArray[np.floating],
    query_az: NDArray[np.floating],
    query_inc: NDArray[np.floating],
    pole: NDArray[np.floating],
    queries: NDArray[np.floating],
) -> NDArray[np.int8]:
    """
    Combination of `SlicedPolygon::numCrossings` and `SlicedPolygon::contains`
    for the non-preprocessed case.

    Performs the check whether a set of query points is inside
    a spherical polygon.
    All inputs are in the query frame.

    Calls `edge_contains`.

    Parameters
    ----------
    vertices_az
        Array of all vertex azimuths [rad]
    vertices_inc
        Array of all vertex inclinations [rad]
    query_az
        Array of all query azimuths [rad]
    query_inc
        Array of all query inclinations [rad]
    pole
        2D array of all cartesian pole coordinates [-]
    queries
        2D array of all cartesian query points [-]

    Returns
    -------
    query_containcode
        Array indicating whether each query point is contained (``1``),
        not contained (``0``), or on an edge (``-1``).
    """
    # initialize output
    m = vertices_az.shape[0] - 1
    n = query_az.shape[0]
    edge_query_containcode = np.empty((m, n), dtype=np.int8)
    # loop over all edges and query points
    for i in prange(m):
        for j in prange(n):
            # check whether a single point crosses a single edge
            edge_query_containcode[i, j] = edge_contains(
                vertices_az[i],
                vertices_az[i + 1],
                vertices_inc[i],
                vertices_inc[i + 1],
                query_az[j],
                query_inc[j],
                pole[i, :],
                pole[i, 2],
                queries[j, :],
            )
    # aggregate the results from all edges
    query_containcode = np.zeros(n, dtype=np.int8)
    for j in prange(n):
        for i in prange(m):
            # check whether the query is directly on an edge,
            # in which case we can finish early
            if edge_query_containcode[i, j] == -1:
                query_containcode[j] = -1
                break
            # else, we keep adding the number of crossings
            else:
                query_containcode[j] += edge_query_containcode[i, j]
        # check if the number of crossings is even, in which case the
        # query point is inside the polygon
        if query_containcode[j] != -1:
            query_containcode[j] = np.int8((query_containcode[j] % 2) == 0)
    # done
    return query_containcode


@njit(cache=True)
def tree_edges_contain_queries(
    vertices_az: NDArray[np.floating],
    vertices_inc: NDArray[np.floating],
    query_az: NDArray[np.floating],
    query_inc: NDArray[np.floating],
    poles: NDArray[np.floating],
    queries: NDArray[np.floating],
    lunes_az: NDArray[np.floating],
    tree: list[NDArray[np.unsignedinteger]],
) -> NDArray[np.int8]:
    """
    Combination of `SlicedPolygon::numCrossings` and `SlicedPolygon::contains`
    for the preprocessed case.

    Performs the check whether a set of query points is inside
    a spherical polygon.
    All inputs are in the query frame.

    Calls `slice_array_get_tree_index` and `edge_contains`.

    Parameters
    ----------
    vertices_az
        Array of all vertex azimuths [rad]
    vertices_inc
        Array of all vertex inclinations [rad]
    query_az
        Array of all query azimuths [rad]
    query_inc
        Array of all query inclinations [rad]
    pole
        2D array of all cartesian pole coordinates [-]
    queries
        2D array of all cartesian query points [-]
    lunes_az
        Array of lune azimuths [rad]
    tree
        In- and output variable that contains the tree

    Returns
    -------
    query_containcode
        Array indicating whether each query point is contained (``1``),
        not contained (``0``), or on an edge (``-1``).
    """
    # initialize output
    n = query_az.shape[0]
    query_containcode = np.zeros(n, dtype=np.int8)
    # loop over all query points
    for j in prange(n):
        # get edges to check from tree
        edges_to_check = tree[slice_array_get_tree_index(query_az[j], lunes_az)]
        # loop over edges to consider
        for i in edges_to_check:
            q_inside_edge = edge_contains(
                vertices_az[i],
                vertices_az[i + 1],
                vertices_inc[i],
                vertices_inc[i + 1],
                query_az[j],
                query_inc[j],
                poles[i, :],
                poles[i, 2],
                queries[j, :],
            )
            # break early if the point is directly on an edge
            if q_inside_edge == -1:
                query_containcode[j] == -1
                break
            # else, keep adding the number of crossings
            else:
                query_containcode[j] += q_inside_edge
        # check if the number of crossings is even, in which case the
        # query point is inside the polygon
        if query_containcode[j] != -1:
            query_containcode[j] = np.int8((query_containcode[j] % 2) == 0)
    # done
    return query_containcode


# part 3: geographic conversions


def spherical2cartesian(incaz: NDArray[np.floating]) -> NDArray[np.floating]:
    """
    Convert spherical inclination/azimuth positions on the unit
    sphere to cartesian coordinates

    Parameters
    ----------
    incaz
        Spherical (inclination/azimuth) coordinates [rad, rad]

    Returns
    -------
    pos
        Cartesian coordinates [-]
    """
    # input shape
    if incaz.ndim == 1:
        incaz = incaz[None, :]
    # readability
    inc, az = incaz[:, 0], incaz[:, 1]
    # unit circle position
    xp = np.sin(inc) * np.cos(az)
    yp = np.sin(inc) * np.sin(az)
    zp = np.cos(inc)
    # scale and return
    return np.stack([xp, yp, zp], axis=1)


def cartesian2spherical(pos: NDArray[np.floating]) -> NDArray[np.floating]:
    """
    Convert cartesian positions on the unit sphere to spherical
    inclination/azimuth positions.

    Parameters
    ----------
    pos
        Cartesian coordinates [-]

    Returns
    -------
    incaz
        Spherical (inclination/azimuth) coordinates [rad, rad]
    """
    # input shape
    if pos.ndim == 1:
        pos = pos[None, :]
    # convert
    inc = np.arccos(pos[:, 2])
    az = np.arctan2(pos[:, 1], pos[:, 0]) % (2 * np.pi)
    # done
    return np.stack([inc, az], axis=1)


def lola2incaz(lola: NDArray[np.floating]) -> NDArray[np.floating]:
    """
    Convert longitude/latitude pairs on the unit sphere into inclination/azimuth.

    Parameters
    ----------
    lola
        Longitude/latitude coordinates [rad]

    Returns
    -------
    incaz
        Inclination/azimuth coordinates [rad]
    """
    # input shape
    if lola.ndim == 1:
        lola = lola[None, :]
    # convert
    inc = np.pi / 2 - lola[:, 1]
    az = lola[:, 0]
    # done
    return np.stack([inc, az], axis=1)
