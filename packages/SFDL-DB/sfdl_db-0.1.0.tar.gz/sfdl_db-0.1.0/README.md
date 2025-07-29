# SFDL_DB

A Python package for generating Same Features, Different Label Skew datasets using KMeans clustering and Davies-Bouldin Score for optimal `k`.

## Installation

```bash
pip install .
```

## Usage

```python
from SFDL_DB import same_features_different_label_skew
import pandas as pd

df = pd.read_csv("your_dataset.csv")
same_features_different_label_skew(df, label_col="Attack", k_optimal=4)
```
