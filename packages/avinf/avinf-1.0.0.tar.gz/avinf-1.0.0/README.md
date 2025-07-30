# avinf: Anytime-Valid Linear Models and Regression Adjusted Inference in Randomized Experiments in Python

**`avinf`** is a Python implementation of **anytime-valid inference** for linear models and ANOVA, based on the methodology developed by Lindon, Ham, Tingley and Bojinov (2025). 

This framework offers sequential analogues of classical tests and confidence intervals that maintain Type I error control and valid coverage across all sample sizes—regardless of when an analyst chooses to stop the experiment.

The method is based on likelihood ratios of invariantly sufficient statistics and yields simple, closed-form expressions involving ordinary least squares (OLS) estimates and standard errors. 

By formally allowing continuous monitoring and early stopping without inflating false positive rates, this approach supports principled sequential experimentation and guards against p-hacking and data snooping. 

This package is a code port of the [`avlm`](https://cran.r-project.org/web/packages/avlm/index.html) R package and provides an accessible python interface using `statsmodels`.

## Features
- Anytime-valid *F*-tests for linear models and ANOVA.
- Works with `statsmodels` OLS models.
- Allows control over inference precision via the `g` parameter.
- Easy conversion from standard linear model outputs.

## Installation

```bash
pip install avinf
```

## Examples
Refer to notebooks in the `examples/notebooks` directory for detailed usage examples.

```
from avinf import avinf
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Load data
df_mtcars = pd.read_csv("https://github.com/Apress/mastering-ml-w-python-in-six-steps/blob/a8f926f5dc7b35b17bf12f14386cd2a66ac2fce3/Chapter_2_Code/Data/mtcars.csv")

# Fit OLS model
model = ols("mpg ~ wt + hp", data=df_mtcars)
model = model.fit()

# Convert to anytime-valid inference object
av_fit = avinf.av_lm.AVLM(model, g=1)

# View summary
print(av_fit.summary())
```

## References
1. Lindon, Ham, Tingley and Bojinov (2025). *Anytime-Valid Linear Models and Regression Adjusted Casual Inference in Randomized Experiments*. arXiv preprint arXiv:2210.08589. https://arxiv.org/pdf/2210.08589

2. It also draws inspiration from the R package by the authors (version 0.1.0.) https://cran.r-project.org/web/packages/avlm/

If you use avinf in your work, please cite the paper and the package(s) appropriately.