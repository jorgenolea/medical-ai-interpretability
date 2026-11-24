# Setup

This guide sets up the development and training environment on AWS, downloads the data
and weights into S3, and connects Cursor to the training machine.

Region used throughout: `eu-central-1` (same region as the S3 bucket, to avoid
cross-region transfer costs).

> Keep your bucket name and AWS account ID out of the repository. Put them in `.env`,
> which is git-ignored.

---

## 1. AWS: permissions

1. In IAM, create a role for EC2 (for example `brain-tumor-uq-ec2`) with a policy that allows
   `s3:ListBucket`, `s3:GetObject` and `s3:PutObject` on your bucket only.
2. Attach this role to every EC2 instance you launch. This avoids storing AWS access keys
   on the machine.
3. Turn on **versioning** for the bucket (S3 console → bucket → Properties).

## 2. AWS: instances

Use two kinds of machine, so you only pay for a GPU when training.

| Purpose | Instance | Notes |
|---|---|---|
| Downloads, data processing, coding | `t3.large` or similar (CPU) | Cheap; can stay on while you work |
| Training | `g5.xlarge` (1× A10G, 24 GB) | Start only for training; stop when done |

For both, use an **AWS Deep Learning AMI (Ubuntu) with PyTorch**, a `gp3` EBS volume of
about 150 GB, and a security group that allows SSH (port 22) **from your IP only**.

Spot instances are much cheaper for training. Training code will checkpoint every epoch
and resume automatically, so interruptions are safe.

Check your service quota for G instances in `eu-central-1` before launching
(Service Quotas → EC2 → "Running On-Demand G and VT instances").

## 3. Connect Cursor to the instance

Add the instance to `~/.ssh/config` on your laptop:

```
Host brain-tumor-uq
    HostName <instance-public-dns>
    User ubuntu
    IdentityFile ~/.ssh/<your-key>.pem
```

In Cursor, run **Remote-SSH: Connect to Host** and choose `brain-tumor-uq`.
Code, data, GPU and terminal (including Claude Code) then all run on the instance.

Note: the public DNS changes each time an instance is stopped and started, unless you
attach an Elastic IP.

## 4. Clone the repository and external code

```bash
git clone https://github.com/jorgenolea/medical-ai-interpretability.git
cd medical-ai-interpretability

# Add external libraries as pinned submodules (first time only)
git submodule add https://github.com/Omid-Nejati/MedViT external/MedViT
git submodule add https://github.com/SamsungLabs/BayesDLL external/BayesDLL
git commit -m "build: add MedViT and BayesDLL as submodules"

# Record the pinned commits in data/MANIFEST.md
git submodule status
```

On later clones: `git clone --recurse-submodules <repo-url>`.

Before committing the submodules, open `external/BayesDLL/` and check whether it
contains a `LICENSE` file. Record what you find in `data/MANIFEST.md`.

## 5. Python environment

```bash
conda env create -f environment.yml
conda activate brain-tumor-uq

# Confirm GPU access
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"

# Compare with MedViT's own requirements and add anything missing
cat external/MedViT/requirements.txt

# Once everything works, lock the environment
conda env export --no-builds > environment.lock.yml
```

Copy `.env.example` to `.env` and fill in your values.

## 6. Download the data into S3

Do this on the CPU instance.

**Kaggle dataset**

1. Kaggle → Settings → API → *Create New Token*. This downloads `kaggle.json`.
2. Copy it to the instance:
   ```bash
   mkdir -p ~/.kaggle && mv kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
   ```
3. Download, record checksums and upload:
   ```bash
   source .env
   mkdir -p ~/downloads && cd ~/downloads
   kaggle datasets download -d masoudnickparvar/brain-tumor-mri-dataset
   sha256sum brain-tumor-mri-dataset.zip
   unzip -q brain-tumor-mri-dataset.zip -d kaggle_brain_tumor_mri
   aws s3 sync kaggle_brain_tumor_mri s3://$S3_BUCKET/data/raw/kaggle_brain_tumor_mri/
   aws s3 cp brain-tumor-mri-dataset.zip s3://$S3_BUCKET/data/archives/
   ```

**Figshare dataset (Cheng et al., 2015)**

1. Find the Figshare record for the brain tumor dataset by Jun Cheng and note its URL,
   version and licence in `data/MANIFEST.md`.
2. Download the files with `wget` (use the download links on the Figshare page),
   record their SHA-256 checksums, then:
   ```bash
   aws s3 sync figshare_cheng2015 s3://$S3_BUCKET/data/raw/figshare_cheng2015/
   ```

## 7. Download the pretrained weights into S3

The MedViT-Base checkpoint is linked from the MedViT README (Google Drive):

```bash
cd ~/downloads
gdown 1Lrfzjf3CK7YOztKa8D6lTUZjYJIiT7_s -O MedViT_base.pth
sha256sum MedViT_base.pth
aws s3 cp MedViT_base.pth s3://$S3_BUCKET/weights/MedViT_base.pth
```

If the file ID no longer works, take the current link from the MedViT README.

## 8. Get data onto a training instance

```bash
source .env
aws s3 sync s3://$S3_BUCKET/data/raw/ $DATA_DIR/raw/
aws s3 cp s3://$S3_BUCKET/weights/MedViT_base.pth $WEIGHTS_DIR/
```

## 9. Experiment tracking (MLflow)

Choose one option and record it here.

- **SageMaker managed MLflow:** create a tracking server in SageMaker Studio, set
  `MLFLOW_TRACKING_URI` to its ARN and install `sagemaker-mlflow`. The server is billed
  while running, so stop it when not in use.
- **Self-hosted:** run `mlflow server` on the CPU instance with `--artifacts-destination`
  pointing to `s3://$S3_BUCKET/mlflow/`, and set `MLFLOW_TRACKING_URI=http://<host>:5000`.

## 10. Daily routine

1. Start the instance, connect with Cursor.
2. `git pull`, `conda activate brain-tumor-uq`, `source .env`.
3. Work, commit, push.
4. **Stop the instance** when finished.
