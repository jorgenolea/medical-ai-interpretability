# Evaluation Protocol

**Version:** 0.1 (draft)
**Status:** Not frozen. This protocol will be frozen before any Phase 2 training run.
After freezing, every change is recorded in the changelog at the end of this file,
with the reason for the change.

The purpose of this document is to fix all design decisions before seeing results,
so that methods are compared fairly and results are not selected after the fact.

---

## 1. Task

Four-class classification of 2D brain MRI slices: glioma, meningioma, pituitary tumor,
no tumor.

## 2. Data

**Primary dataset:** Brain Tumor MRI Dataset (Nickparvar, 2021, Kaggle), all images from
both the original `Training` and `Testing` folders, pooled.

**Auxiliary dataset:** Figshare brain tumor dataset (Cheng et al., 2015). Used for tumor
masks in the interpretability analysis (Section 8). Images are matched to the primary
dataset by perceptual hash.

**Known limitation:** the primary dataset has no patient identifiers, so a patient-level
split is not possible. This is stated as a limitation in all reporting.

## 3. Deduplication and splitting

1. Compute a perceptual hash (pHash) for every image.
2. Treat two images as duplicates if their Hamming distance is at most a threshold *T*.
   *T* is chosen once by manually inspecting candidate pairs, and documented with examples.
3. Group duplicates into clusters. All images in a cluster go to the same split.
4. Report: number of duplicate clusters, how many crossed the original train/test folders,
   and any clusters with conflicting labels (these are removed and counted).
5. Split the deduplicated clusters into train / validation / test = 70 / 15 / 15,
   stratified by class, with seed 0.
6. Save the split as `data/splits/split_v1.csv` (columns: relative path, label, split,
   cluster id, SHA-256). This file is never regenerated.

## 4. Preprocessing and augmentation

- Read as grayscale, bilateral filter (d=2, sigmaColor=50, sigmaSpace=50),
  `COLORMAP_BONE`, convert to RGB, resize to 224×224, normalise with mean 0.5 and std 0.5.
  Applied identically to all splits.
- Training augmentation only: random horizontal flip, random rotation (±15°),
  random resized crop (scale 0.8–1.0).
- Vertical flips are not used, because they produce anatomically implausible images.

## 5. Methods

All methods start from the same MedViT-Base weights (ImageNet-1K pretrained),
with a new 4-class linear head.

| ID | Method | Notes |
|---|---|---|
| M1 | Standard fine-tuning | Deterministic baseline |
| M2 | M1 + temperature scaling | Temperature fitted on the validation set by minimising NLL |
| M3 | Deep ensemble | The 5 seeds of M1 combined |
| M4 | MC dropout | Dropout kept active at test time (dropout placement to be confirmed in Phase 0) |
| M5 | Variational inference (BayesDLL) | Pretrained weights as prior mean |

## 6. Training and model selection

- Same optimiser family (AdamW), same maximum epoch budget and same data loaders for all methods.
- Validation runs every epoch for every method.
- Model selection criterion: lowest validation NLL. The best checkpoint is used for testing.
- Early stopping: patience counted in epochs, identical for all methods.
- Hyperparameter tuning: each method gets the same small tuning budget on the validation set
  (grids defined in `configs/` before tuning starts). For M5 this includes the KL weight
  (`kld`), since the BayesDLL authors use different values for different settings.
- Seeds: 0, 1, 2, 3, 4 for every method.

## 7. Evaluation

**Prediction rule.** Deterministic methods use one forward pass. M3 averages softmax
probabilities over ensemble members. M4 and M5 average softmax probabilities over
*S* = 30 Monte Carlo samples (sensitivity to *S* reported separately). For M5, the
posterior mean prediction is also reported for comparison.

**Primary metrics:** negative log-likelihood (NLL), expected calibration error
(ECE, 15 equal-width bins).

**Secondary metrics:** accuracy, macro-F1, one-vs-rest AUC, Brier score,
maximum calibration error (reported together with the number of samples in the worst bin),
reliability diagrams.

**Usefulness of uncertainty (Phase 3):**
- Misclassification detection: AUROC of predictive entropy for separating correct and
  incorrect predictions.
- Selective prediction: accuracy–rejection curves and area under the risk–coverage curve.
- For M3–M5: decomposition into total, aleatoric (expected entropy) and epistemic
  (mutual information) uncertainty.

**Statistics.** Mean ± standard deviation over seeds. 95% bootstrap confidence intervals
on the test set. Paired comparisons of accuracy with McNemar's test; paired comparisons
of NLL with a paired bootstrap.

## 8. Interpretability

- Grad-CAM on a fixed list of test images, identical for all methods, defined before
  computing any heatmap.
- For images matched to Figshare masks: energy inside the tumor mask and pointing-game accuracy.
- For M4 and M5: Grad-CAM averaged over posterior samples, plus the pixel-wise variance
  across samples.
- Images are un-normalised before display.

## 9. Questions this protocol is designed to answer

These are stated in advance and reported whatever the outcome.

1. Does M5 achieve lower NLL and ECE than M1?
2. Does M5 achieve lower NLL and ECE than M2 and M3?
3. Does any method's uncertainty detect misclassifications better than M1's softmax confidence?
4. Do Grad-CAM maps localise tumors, and does this differ between methods?

## 10. Reproducibility

- All runs logged to MLflow with config, seed, git commit hash and environment.
- External code pinned by git submodule commit.
- Data recorded in `data/MANIFEST.md` with source, licence, download date and checksums.

---

## Changelog

| Date | Version | Change | Reason |
|---|---|---|---|
| | 0.1 | Initial draft | |
