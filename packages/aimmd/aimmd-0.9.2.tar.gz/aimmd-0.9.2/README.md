# aimmd

## Synopsis

aimmd - AI for Molecular Mechanism Discovery: Machine learning the reaction coordinate from shooting results.

## Code Example

Please see the jupyter notebooks in the `examples` folder.

## Motivation

This project exists because finding reaction coordinates of molecular systems is a great way of understanding how they work.

## Installation

aimmd runs its TPS simulations either through [asyncmd] (if managing and learning from many simulations simultaneously, possibly on a HPC cluster) or through [openpathsampling] (in the sequential case). [openpathsampling] and [asyncmd] can both easily be installed via pip and are automatically installed when you install aimmd with pip.

Note, that for [asyncmd] and/or [openpathsampling] to work you need to install a molecular dynamics engine to perform the trajectory integration. In [asyncmd] the only currently supported engine is [gromacs], while [openpathsampling] can use both [gromacs] and [openMM] (but [openMM] is highly recommended).

In addition to [asyncmd] and/or [openpathsampling] to run the TPS simulations you need to install at least one machine learning backend (to actually learn the committor/ the reaction coordinate). aimmd supports multiple different backends and can easily be extended to more. The backend is used to define the underlying machine learning models architecture and is used to fit the model. It naturally also defines the type of the model, i.e. neural network, symbolic regresssion, etc.
Currently supported backends are (model types in brackets):

- [pytorch] (neural network) : [Recommended for steering and learning from simulations iteratively]
- [tensorflow]/keras (neural network) : [Mostly included for legacy reasons]
- [dcgpy] (symbolic regression expressions) [Currently no steering and learning from simulations on-the-fly possible; recommended to build low dimensional interpretable models of the committor]

You should be able to install any of them using pip and/or conda. Please refer to their respective documentations for detailed installation instructions.

### pip install from PyPi

aimmd is published on [PyPi], installing is as easy as:

```bash
pip install aimmd
```

### pip install directly from the repository

To install an editable copy of aimmd, cd whereever you want to keep your local copy of aimmd, clone the repository and install aimmd using pip, e.g.

```bash
git clone https://github.com/bio-phys/aimmd.git
pip install -e aimmd/
```

### TLDR

- You will need to install at least one of the machine learning backends, i.e. [pytorch] (recommended for steering and learning from simulations iteratively), [tensorflow] and/or [dcgpy] (recommended for building low dimensional interpretable models).
- For using the `aimmd.distributed` module and steering many simulations simultaneously (locally or on a HPC cluster) you need a working installation of [asyncmd] (which uses [gromacs] as MD engine).
- You might want to install additional engines for use with the sequential aimmd code building on [openpathsampling], e.g. [openMM].


## Tests

Tests use pytest. Use e.g. `pytest .` while in the toplevel directory of the repository to run them.

## Contributions

Contributions are welcome! Please feel free to open an [issue](https://github.com/bio-phys/aimmd/issues) or [pull request](https://github.com/bio-phys/aimmd/pulls) if you discover any bugs or want to propose a missing feature.

## License

GPL v3

---
<sub>This README.md is printed from 100% recycled electrons.</sub>

[asyncmd]: https://github.com/bio-phys/asyncmd
[dcgpy]: http://darioizzo.github.io/dcgp/
[GROMACS]: http://www.gromacs.org/
[openMM]: http://openmm.org/
[openpathsampling]: http://openpathsampling.org/latest/
[PyPi]: https://pypi.org/project/aimmd/
[pytorch]: https://pytorch.org
[tensorflow]: https://www.tensorflow.org
