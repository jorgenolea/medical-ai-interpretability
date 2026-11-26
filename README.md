# Uncertainty and Interpretability in Brain Tumor MRI Classification

**A rigorous re-evaluation of Bayesian fine-tuning for a pretrained vision transformer (MedViT)**

> **Status: work in progress.** See the [roadmap](#roadmap) for what is done and what is still running.

## Overview

This project revisits my MSc thesis (University of London, 2024), which applied Bayesian fine-tuning (variational inference via [BayesDLL](https://github.com/SamsungLabs/BayesDLL)) to [MedViT](https://github.com/Omid-Nejati/MedViT) for four-class brain tumor classification (glioma, meningioma, pituitary, no tumor).

After submission I reviewed the thesis and its code critically and identified several methodological limitations. This repository re-runs the study under a single, pre-specified evaluation protocol, so that every method is trained, selected and evaluated in the same way.

**Research questions**

1. Does Bayesian fine-tuning improve calibration and predictive uncertainty compared with standard fine-tuning and simpler alternatives (temperature scaling, deep ensembles, MC dropout)?
2. Are the uncertainty estimates useful in practice, for example to flag incorrect predictions for clinician review?
3. Do Grad-CAM explanations localise tumors, and how do they vary across posterior samples?

## What changed since the thesis

| Limitation in the original thesis | How this project addresses it |
|---|---|
| Calibration metrics computed only for the Bayesian model | All methods evaluated with the same metrics, including temperature scaling |
| Bayesian test predictions used a single deterministic forward pass | Posterior predictive computed by averaging over Monte Carlo samples |
| Models trained and evaluated on different data splits and epoch budgets | One fixed, saved split and one training protocol for all methods |
| Single run, no confidence intervals | 5 seeds, bootstrap confidence intervals, paired significance tests |
| No check for duplicate images across splits | Perceptual-hash deduplication before splitting |
| Uncertainty reported but not used | Misclassification detection and accuracy–rejection analysis |
| Grad-CAM assessed qualitatively on two images | Quantitative localisation against tumor masks |

The original thesis and notebook are not included in this repository. The full protocol is in [`PROTOCOL.md`](PROTOCOL.md).

## Repository structure

```
├── CLAUDE.md    Instructions for AI coding assistants
├── configs/     One YAML config per method
├── data/        Split files and data manifest (no images)
├── src/         Data, models, methods, evaluation, uncertainty, Grad-CAM
├── scripts/     Entry points: training, evaluation, figures
├── tests/       Unit tests for splits and metrics
├── results/     Final tables and figures
└── external/    MedViT and BayesDLL as pinned git submodules (planned)
```

## Getting started

Create the Python environment from [`environment.yml`](environment.yml). Data sources, licences and checksums are listed in [`data/MANIFEST.md`](data/MANIFEST.md). MedViT and BayesDLL will be included as pinned git submodules under `external/`.

## Results

*To be added as experiments complete.*

## Roadmap

| Phase | Description | Status |
|---|---|---|
| 0 | Evaluation protocol written and frozen | In progress |
| 1 | Data integrity: deduplication and fixed split | Planned |
| 2 | Unified training and evaluation of all methods | Planned |
| 3 | Usefulness of uncertainty (misclassification detection, selective prediction) | Planned |
| 4 | Quantitative interpretability (Grad-CAM vs. tumor masks) | Planned |
| 5 | Technical report | Planned |

## Data

This project uses publicly available datasets. No images are stored in this repository.

- **Brain Tumor MRI Dataset** (Nickparvar, 2021), Kaggle. DOI: 10.34740/KAGGLE/DSV/2645886
- **Figshare brain tumor dataset** (Cheng et al., 2015), used for tumor masks.

Sources, licences and checksums are recorded in [`data/MANIFEST.md`](data/MANIFEST.md).

## Acknowledgements and citations

- Manzari, O. N. et al. (2023). *MedViT: A robust vision transformer for generalized medical image classification.* Computers in Biology and Medicine, 157, 106791.
- Kim, M. and Hospedales, T. (2023). *BayesDLL: Bayesian Deep Learning Library.* arXiv:2309.12928.
- Cheng, J. et al. (2015). *Enhanced performance of brain tumor classification via tumor region augmentation and partition.* PLoS ONE, 10(10).

## Use of AI tools

AI coding assistants (Claude, via Cursor and Claude Code) were used to help write and review code. The rules they follow in this repository are in [`CLAUDE.md`](CLAUDE.md). All experimental design decisions, results and interpretations are my own, and all code was reviewed before being committed.

## Disclaimer

This is a research project. It is not a medical device and must not be used for clinical diagnosis.

## Licence

All rights reserved. No licence is granted for use, copying, modification or distribution of the code in this repository at this stage. Third-party libraries and datasets are subject to their own licences.
