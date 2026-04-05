SPDX-License-Identifier: GPL-3.0-or-later ( https://www.gnu.org/licenses/gpl-3.0.txt )

These are datasets used by the MLLite QA process. They are used to test/validate classification, regression and preprocessing algorithms implemented in MLLite.

These datasets are automatically generated from their original sources.

A single python script (src/save_all_datasets.py) is used to perform some preprocessing and save the data. This script does not depend on MLLite and uses only open source software. The generated datasets are saved in the 'data' directory.

Some datasets are generated to push the limits : Too many classes (64), too many features (1024), ... These are used to analyze the complexity of the algorithms.

Each original dataset is preprocessed and saved in different forms/flavors. Flavors are designed to help with a specific modeling issue.

As of 2026-01-01, the following flavors are available :

1. Original : Full dataset. Contains only numerical data (can be used with regression and classification).
2. Raw : Full dataset. Contains non-numerical data (can be used with preprocessing).
3. Sampled : random sample of N / 8 rows, where N is the size of the datasets.
4. Medium : random sample of 512 rows.
5. Small : random sample of 64 rows.
6. Tiny : random sample of 16 rows.
7. Quantized : numerical columns are quantized using sklearn.QuantileTransformer(n_quantiles=10).
8. Embedded CSV : a C++ CSV-like string that can be included in a source file and compiled. available in different sizes. 
9. Embedded : a C++ std::vector-based array that can be included in a source file and compiled. available in different sizes. 
10. Missing : data are artificially deleted in random places, impacting 5% of the dataset.

This is an evolving process. more flavors/datasets can be added when needed. Your feedback is welcome.

Most of these datasets are originally from sklearn.datasets, kddcup99, kdd-cup-2009, cran R packages as well as various public sources. sources are mentioned in the generating script when available.

Files above 100MB are not allowed in github. We decided to not upload datasets above 100K rows (very long datatsets are truncated). Therefore, serious length-based performance tests cannot be performed on these datasets. 

These datasets are used in the MLLite QA process every time a software feature is tested. Pre-commit tests are needed to validate software changes. Some tests are tailored to use a flavor that reduces the test run time. New tests can trigger the creation of new flavors.

