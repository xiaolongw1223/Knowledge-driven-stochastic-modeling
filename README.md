<img src="docs/images/mineralx_logo.png" width=70% align="middle">

# Stochastic modeling of geological geometry features
**[summary](#summary) | [features](#features) | [usage](#usage) | [citations](#citations) | [issues](#issues)**

[![DOI](https://img.shields.io/badge/DOI-10.1190%2FGEM2024--091.1-blue.svg)](https://doi.org/10.1190/GEM2024-091.1)

## Summary

#### Plain language summary:

Understanding the shape and geometry of the subsurface structures is very important in geosciences. Various data sources have been employed to infer the geometric features of geological units. The framework developed in our study allows to include drawings of geological diagrams, which represent expert knowledge, into stochastic simulations. The constructed 3D models are aligned with geological diagram, drillhole data, outcrop contacts, and geophysics. We quantify the uncertainty of geometric characteristics for constructed models.

<img src="docs/images/animation_drillholes.gif" width=50% align="right">

#### Authors:

Xiaolong Wei (xwei2@stanford.edu)

David Zhen Yin (yinzhen@stanford.edu)

Wilson Bonner (wilson.bonner@koboldmetals.com)

Lijing Wang(lijing.wang@uconn.edu)

Jef Caers (jcaers@stanford.edu)

#### Acknowledgments:

[Kobold Metals](https://www.koboldmetals.com/)

<br>
<br>

## Features

This package has the following features:

- Perform 2D/3D level-set Monte Carlo sampling to construct geological models
- Construct models constrained by drillholes, outcrop contacts, and geological diagrams
- Impose constraints individually or jointly
- Quantify uncertainty of the constructed models
- Simulate gravity and magnetic data for the constructed models using [SimPEG](https://simpeg.xyz/) (ongoing)
- Falsify geological hypotheses (ongoing)

## Usage

To run the package locally, you need to have python installed, followed by the installation of dependencies:
```
pip install -r requirements.txt
```

## Citations

If you use script in your work, please cite:

## Issues

Please [make an issue](https://github.com/xiaolongw1223/Knowledge-driven-stochastic-modeling/issues) if you encounter any problems while trying to run the notebooks.

Or contact Xiaolong Wei directly via email.
