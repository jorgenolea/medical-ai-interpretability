# CLAUDE.md

Instructions for AI coding assistants working in this repository.

## Project context

This project re-does my MSc thesis on Bayesian fine-tuning of MedViT for four-class
brain tumor MRI classification, under a rigorous and fair evaluation protocol.
The goal is a reproducible, portfolio-quality research repository.

Read `PROTOCOL.md` before making any change that affects data, training or evaluation.
The protocol is the source of truth. If a request conflicts with it, stop and say so.

## Non-negotiable rules

1. **One split for everything.** All models read the split files in `data/splits/`.
   Never re-split, re-shuffle or filter data inside training code.
2. **One evaluation path.** Every model is evaluated only through `src/evaluate.py`.
   Do not write method-specific evaluation code.
3. **Best checkpoint only.** Test-time evaluation always loads the checkpoint with the
   best validation score as defined in `PROTOCOL.md`, never the last epoch.
4. **Stochastic methods average over samples.** For VI, MC dropout and ensembles,
   the prediction is the mean of the softmax probabilities over samples or members.
   A single deterministic forward pass is never used as the Bayesian prediction.
5. **No hard-coded hyperparameters.** All values come from `configs/*.yaml`.
6. **Every run is tracked.** Log config, seed, git commit hash, metrics and artifacts
   to MLflow. A run that is not logged did not happen.
7. **Never touch the test set during development or tuning.** Test evaluation runs
   only after the protocol is frozen and model selection is complete.

## Security and data

- Never commit data, images, model weights, checkpoints or MLflow runs.
- Never commit secrets, credentials, `.env` files, bucket names or AWS account IDs.
  Read them from environment variables (see `.env.example`).
- Raw data in S3 (`data/raw/`) is read-only. Never write to it.

## External libraries

- MedViT and BayesDLL live in `external/` as pinned git submodules. Do not edit them.
  Wrap them in `src/` instead.
- Before writing any code that uses BayesDLL, read `external/BayesDLL/bayesdll/vi.py`
  (and `mc_dropout.py` if relevant) and explain:
  - where the variational mean and variance parameters are stored,
  - how weights are sampled during training and evaluation,
  - how the KL term is scaled (`kld`, dataset size `ND`),
  - what `runner.evaluate` returns and whether it averages over samples.
  Write this explanation to `docs/BAYESDLL_NOTES.md` and wait for my review.

## Coding standards

- Python 3.11, type hints, docstrings on public functions.
- Small, testable functions. Put shared logic in `src/`, entry points in `scripts/`.
- Add or update tests in `tests/` for any change to data splitting or metrics.
  Run `pytest` before proposing a commit.
- Set all random seeds (Python, NumPy, PyTorch) from the config.
- Clear, specific commit messages (for example, `data: add pHash deduplication`).

## How to work with me

- Explain what you plan to change before making large edits.
- Ask before installing new dependencies or changing `PROTOCOL.md`.
- Never write or edit result numbers, figures or claims in the README or report.
  Results come only from logged runs.
- If you are unsure how something works, say so rather than guessing.
