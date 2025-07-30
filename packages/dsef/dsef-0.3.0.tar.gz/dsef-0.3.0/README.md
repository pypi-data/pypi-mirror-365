<h1 align="center">
    <img alt="DSEF" ttle="DSEF" src="https://raw.githubusercontent.com/Autonomi-USN/DSEF/refs/heads/main/assets/dsef_logo.png?s=200&v=4" />
    <p>Direct Step Edge Follower</p>
</h1>

![ci build](https://github.com/Autonomi-USN/DSEF/actions/workflows/pypi-publish.yml/badge.svg)
![Python Version](https://img.shields.io/pypi/pyversions/dsef)
![Downloads](https://img.shields.io/pypi/dm/dsef)
![PyPI - License](https://img.shields.io/pypi/l/dsef)
[![PyPI version](https://badge.fury.io/py/dsef.svg)](https://badge.fury.io/py/dsef)

# DSEF Package

The [Direct Step Edge Follower (DSEF)](https://www.researchgate.net/publication/390370984_Direct_Step_Edge_Follower_a_novel_edge_follower_algorithm_applied_to_solar_panels_inspections_with_Unmanned_Aerial_Vehicles) is a edge-following algorithm designed for high-precision edge detection with low computational cost. It employs stepwise directional refinement and kernel-based statistical testing to enhance accuracy, particularly in challenging lighting conditions.

## Citation

To cite DSEF in your research, please cite as:

```bibtex
@article{Sivertsen2025DSEF,
  author    = {Agnar Sivertsen and Fabio A. A. Andrade and Marcos Moura and Carlos A. M. Correia and Mariane R. Petraglia},
  title     = {Direct Step Edge Follower: a novel edge follower algorithm applied to solar panels inspections with Unmanned Aerial Vehicles},
  journal   = {Preprint},
  year      = {2025},
  month     = {April},
  url       = {https://www.researchgate.net/publication/390370984_Direct_Step_Edge_Follower_a_novel_edge_follower_algorithm_applied_to_solar_panels_inspections_with_Unmanned_Aerial_Vehicles}
}

```

## Speeds

The DSEF can work in three modes, or speeds, are described in the table below:

| **Parameter**                     | **Low**               | **Medium**            | **High**              |
| --------------------------------- | --------------------- | --------------------- | --------------------- |
| $\Delta s$ _(EdgeSearch step)_    | dist ⁄ 80             | dist ⁄ 60             | dist ⁄ 40             |
| $\Delta \ell$ _(EdgeFollow step)_ | diag ⁄ 200            | diag ⁄ 100            | diag ⁄ 50             |
| $\Delta \theta$ _(Angle Res.)_    | $\Omega$ ⁄ 90         | 4 $\Omega$ ⁄ 90       | 10 $\Omega$ ⁄ 90      |
| $N_{\theta}$ _(LUT size)_         | 360 ⁄ $\Delta \theta$ | 360 ⁄ $\Delta \theta$ | 360 ⁄ $\Delta \theta$ |

Where $\mathrm{dist} = \sqrt{(u_{\mathrm{end}}-u_{\mathrm{start}})^2 + 
(v_{\mathrm{end}}-v_{\mathrm{start}})^2}$ and $\mathrm{diag} = \sqrt{(\mathrm{Width})^2 + (\mathrm{Height})^2}$

Lower speeds have more accuracy, due to the smaller steps, and higher speeds can have less accuracy but are faster.

## How to use

The examples of DSEF can be found in the following links:

[Simple Implementation of DSEF Search and Follow](https://github.com/Autonomi-USN/DSEF/blob/main/docs/Simple-DSEF.ipynb)

[Implementation and Comparison between the different Speed Modes in DSEF](https://github.com/Autonomi-USN/DSEF/blob/main/docs/Speeds.ipynb)
