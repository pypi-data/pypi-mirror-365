# fastrdp


<a href="https://pypi.org/project/fastrdp/">
<img src="https://img.shields.io/pypi/v/fastrdp" alt="PyPI Latest Release"/>
</a>

The *fastrdp* package contains an implementation of the
[Ramer–Douglas–Peucker
algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm)
for reducing the number of points in a curve.

# Example

There are two functions in the *fastrdp* package: `rdp` that returns the
points by the RDP algorithm and `rdp_index` that returns the indices of
the returned points in the input.

Here is an example from the Wikipedia page linked to above with a
description of the algorithm. The original line is black and the
approximating line is red.

``` python
import matplotlib.pyplot as plt
import numpy as np
import fastrdp

x = np.linspace(0, 5, 10_000)
y = np.exp(-x) * np.cos(2 * np.pi * x)
x_new, y_new = fastrdp.rdp(x, y, 0.06)

fig, ax = plt.subplots()
ax.plot(x, y, color='black', linewidth=2.0)
ax.plot(x_new, y_new, linestyle='dashed', color='red')
plt.show()
```

![](README_files/figure-commonmark/cell-2-output-1.png)

# Performance

Here we compare the performance of *fastrdp* with that of a pure Python
implementation. The example above is executed with *fastrdp* in less
than a millisecond on my machine

``` python
from timeit import timeit
timeit(lambda: fastrdp.rdp(x, y, 0.1), number=10_000)
```

    0.6944626589975087

The pure Python implementation in the [*rdp*
package](https://pypi.org/project/rdp) takes longer to execute a single
run than *fastrdp* takes to execute 10.000 runs.

``` python
import rdp
z = np.column_stack((x, y))
timeit(lambda: rdp.rdp(z, epsilon=0.1), number=1)
```

    0.758994490999612

To illustrate how *fastrdp* scales consider the following graph that
shows execution time for an increasing number of point for both random
and structured data. The latter means that the output of `rdp` is
**much** smaller than the input. The figure is produced with the script
in the `performance` folder.

![](performance/performance.png)

# Compilation

To specify package metadata *fastrdp* is using the contemporary
`pyproject.toml`. Execute the following commands to build and install
*fastrdp*

``` bash
pip install .
```

If you want an editable installation, then add a `-e` to the last
command. To also install the optional dependencies used for development
add a little extra:

``` bash
pip install -e '.[dev]'
```

The single quotes are needed in zsh, but is perhaps superfluous in other
shells.

# README

This README is made from the [Quarto](https://quarto.org) document
`README.qmd` with this command

``` {bash}
quarto render README.qmd --to gfm --output README.md
```

# Acknowledgements

Setting up package metadata to build and compile *fastrdp* is inspired
by the [pybind11 example
package](https://github.com/pybind/python_example).
