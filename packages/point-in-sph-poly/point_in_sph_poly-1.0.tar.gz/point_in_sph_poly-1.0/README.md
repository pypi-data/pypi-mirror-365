# Python implementation of "Point in Spherical Polygon Algorithm Implementation"

Python implementation for the original code
[sphericalpolygon](https://github.com/ryanketzner/sphericalpolygon)
as published in the paper:

> Ryan Ketzner, Vinay Ravindra, Michael Bramble,
> *A robust, fast, and accurate algorithm for point in spherical polygon*
> *classification with applications in geoscience and remote sensing*,
> Computers & Geosciences, Volume 167, 2022, 105185, ISSN 0098-3004,
> https://doi.org/10.1016/j.cageo.2022.105185

The code is runtime-optimized using [Numba](https://numba.pydata.org/) to
avoid severe performance penalties due to all the loops in the code.
The output of this package is tested against the three test cases in
the original paper and confirmed to yield the same results.
However, since I did try to extract only the necessary components
and make the functions more amenable for Python code, I cannot guarantee that
I did not introduce some other mistakes - please let me know in the
issues if you find a bug.

## Installation

Since this code is pure Python, only the requirements specified in
the `pyproject.toml` are necessary to run the code. The following
should take care of everything:

```bash
# optional: create a virtual environment with numpy, scipy, and numba,
# otherwise let pip handle the installation of the requirements
# option 1: install from PyPI
pip install point-in-sph-poly
# OR option 2: install from repository
git clone https://github.com/tobiscode/pisp.git
cd pisp
pip install .
```

## Usage

The following illustrates a small example (where preprocessing is not
useful):

```python
>>> # imports
>>> import numpy as np
>>> from pisp import SphericalPolygon
>>> # all coordinates as lon, lat pairs [rad]
>>> vertices = np.array([[-0.2, -0.1, 0.1, 0.2, 0.1, -0.2],
...                      [-0.4, -0.4, -0.2, 0, 0, -0.4]]).T
>>> inside = np.array([0, -0.2])
>>> queries = np.array([[0.05, -0.2], [-0.2, -0.4], [0.15, -0.001], [-0.1, -0.1]])
>>> # construct
>>> sp = SphericalPolygon.from_lon_lat(vertices, inside)
>>> # run everything once to compile the functions
>>> # this should only be necessary upon first installation due to caching
>>> _ = sp.contains_lola(queries)
>>> sp.preprocess()
>>> _ = sp.contains_lola(queries)
>>> # run again after compilation
>>> sp = SphericalPolygon.from_lon_lat(vertices, inside)
>>> # turn on timing (optional)
>>> sp.timeit = True
>>> # run with and without preprocessing
>>> result_without = sp.contains_lola(queries)
Processing (w/o preprocessing) took 35.4 µs (8.9 µs per point)
>>> sp.preprocess()
Preprocessing took 64.5 µs (12.9 µs per edge)
>>> result_with = sp.contains_lola(queries)
Processing (w/ preprocessing) took 31.7 µs (7.9 µs per point)
>>> print(f"{result_with=}")
result_with=array([1, 1, 1, 0], dtype=int8)
```

The output is an array indicating where for each query point:

- `1` means contained,
- `0` means not contained,
- and `-1` means the query point is exactly on an edge.

Note that if you have a complex polygon with lots of query points to check,
you can also let the functions compile using a simpler polygon and fewer points
(e.g., this example).
As long as the inputs have the same data type, Numba will not have to compile again.

## Documentation

An API documentation is generated into the `docs` folder. It is hosted on GitHub publicly
at [tobiscode.github.io/pisp](https://tobiscode.github.io/pisp), but you can
also read it locally, e.g., by running `python -m http.server 8080 --bind 127.0.0.1`
from with the documentation folder and then opening a browser. It is created using
`pdoc -d numpy -o docs/ pisp.py`.

## Runtime comparison with `sphericalpolygon`

These runtime comparisons were made on an 10-core virtual machine with 32 GB RAM,
using the example data and comparison scripts provided by the original code.
Note that the JIT-compilation duration of Numba-optimized Python code is not
considered, and that the timers are not exactly at the places as they are in
the original code.
Nevertheless, these values should show the improved (if not comparable)
performance of the Python implementation.

| Case       | Step                    | C++ [µs] | Python [µs] |
|:-----------|:------------------------|---------:|------------:|
| Square     | Query w/o preprocessing |    10108 |        1257 |
|            | Preprocessing           |       40 |          20 |
|            | Query w/ preprocessing  |     8041 |        1507 |
| Radiometer | Query w/o preprocessing |   237683 |       71195 |
|            | Preprocessing           |     1159 |         281 |
|            | Query w/ preprocessing  |    10094 |        1976 |
| Tennessee  | Query w/o preprocessing | 24322600 |     8044063 |
|            | Preprocessing           |   163709 |       25938 |
|            | Query w/ preprocessing  |    10526 |        3121 |

## License

Copyright 2025 Tobias Köhne

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
