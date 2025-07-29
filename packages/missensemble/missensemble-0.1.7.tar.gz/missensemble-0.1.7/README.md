# MissEnsemble

MissEnsemble implements the popular Missforest algorithm for imputing missing values, but it generalizes it to different ensemble methods as well. It follows the scikit-learn API. Ensemble methods currently supported: 

- Random Forests
- XGBoost

## Setup
Download it from pypi with:

```bash
pip install missensemble
```

## Usage (Example)

```python
from missensemble_class_dev import MissEnsemble

# Initialize the MissEnsemble class
miss_ensemble = MissEnsemble(n_iter=10, categorical_vars=['cat_var1', 'cat_var2'], ordinal_vars=['ord_var'], numerical_vars=['num_var1', 'num_var2'])

# Fit and transform the data
imputed_data = miss_ensemble.fit_transform(data)
```

## Dependencies

- numpy
- pandas
- scikit-learn
- xgboost
- seaborn
- matplotlib

## Parameters

- `n_iter` (int): The number of iterations to perform for imputation.
- `categorical_vars` (list): A list of column names representing categorical variables.
- `ordinal_vars` (list): A list of column names representing ordinal variables.
- `numerical_vars` (list): A list of column names representing numerical variables.
- `ens_method` (str, optional) : The ensemble method to use for imputation. Default is 'forest'.
- `n_estimators` (int, optional) : The number of estimators to use in the ensemble method. Default is 100.
- `random_state` (in, optional) : The random state for reproducibility. Default is 42.
- `print_criteria` (bool, optional) : Whether to print the imputation criteria during fitting. Default is True.


## Cool things about the package
- The package handles different types of input values (e.g., strings, numbers, etc) natively. The only you have to do is to specify which column names belong to which categorics (i.e., numerical, categorical or ordinal variable).

- The package implements more than one ensemble methods (Random Forests and XGBoost currently).

- The package has built-in visualization functions for convergence and missing value validation (in case the original values are known).

## Literature
Stekhoven, D. J., & Bühlmann, P. (2012). MissForest—non-parametric missing value imputation for mixed-type data. Bioinformatics, 28(1), 112-118.