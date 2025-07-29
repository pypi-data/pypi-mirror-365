<div align="center">
    <img src="https://github.com/KempnerInstitute/lueur/blob/main/docs/assets/logo.png?raw=True" width="45%" alt="Lueur logo" />
</div>

<br>

<div align="center">
    <img src="https://img.shields.io/badge/Python-3.8, 3.9, 3.10-efefef">
    <img alt="PyLint" src="https://github.com/KempnerInstitute/lueur/actions/workflows/lint.yml/badge.svg">
    <img alt="Tox" src="https://github.com/KempnerInstitute/lueur/actions/workflows/tox.yml/badge.svg">
    <img alt="Pypi" src="https://github.com/KempnerInstitute/lueur/actions/workflows/publish.yml/badge.svg">
    <img src="https://img.shields.io/badge/Documentation-Online-EE9D35">
    <img alt="Pepy" src="https://static.pepy.tech/badge/lueur">
    <img src="https://img.shields.io/badge/License-MIT-efefef">
</div>

---

# Lueur

**Lueur** (pronounced *ly.œʁ*) means "faint glow" in French. It is a minimal, modular toolbox for NeuroInterpretability.

Lueur is intended for researchers interested in understanding representations in artificial neural networks, particularly in contexts inspired by neuroscience. It collects a set of lightweight tools for attribution, feature visualization and concept extraction.

While deep networks are not biological systems, their internal structures often raise questions that intersect with those asked in cognitive science and neuroscience. As such models become more capable, it is increasingly important to study not only what they achieve, but how they structure information, and what kinds of functions they implicitly compute.

Lueur provides a small, hackable set of tools to aid in that investigation.

## Scope

Lueur is built around PyTorch and provides tools for:

- Attribution methods (saliency, integrated gradients, smoothgrads, rise, ...)
- Feature visualization (fourier, maco, ...)
- Sparse dictionary learning (SAE variants for concept extraction)
- Visualization and analysis utilities
- Tutorials and reproducible interpretability workflows

## Notebooks and Tutorials

The main companion notebooks and reports are hosted in the following repository:
[serre-lab/ExplainableNeuro](https://github.com/serre-lab/ExplainableNeuro)

## Installation

```bash
pip install lueur
```

# 👏 Credits
<div align="right">
  <picture>
    <source srcset="https://kempnerinstitute.harvard.edu/app/uploads/2024/08/Kempner-logo_Full-Color-Kempner-and-Harvard-Logo-Lockup-2048x552.png"  width="60%" align="right">
    <img  style="background-color: rgba(255, 255, 255, 0.8)" alt="Kempner Logo" src="https://kempnerinstitute.harvard.edu/app/uploads/2024/08/Kempner-logo_Full-Color-Kempner-and-Harvard-Logo-Lockup-2048x552.png" width="60%" align="right">
  </picture>
</div>

This work has been made possible in part by the generous support provided by the Kempner Institute at Harvard University. The institute, established through a gift from the Chan Zuckerberg Initiative Foundation, is dedicated to advancing research in natural and artificial intelligence. The resources and commitment of the Kempner Institute have been instrumental in the development and completion of this project.


# Authors

- [Thomas Fel](https://thomasfel.me) - tfel@g.harvard.edu, Kempner Research Fellow, Harvard University.