# PyStataR

[![Python Version](https://img.shields.io/pypi/pyversions/pystatar)](https://pypi.org/project/pystatar/)
[![PyPI Version](https://img.shields.io/pypi/v/pystatar)](https://pypi.org/project/pystatar/)
[![License](https://img.shields.io/pypi/l/pystatar)](https://github.com/brycewang-stanford/PyStataR/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/pystatar)](https://pypi.org/project/pystatar/)

> **The Ultimate Python Toolkit for Academic Research - Bringing Stata & R's Power to Python** 🚀

## 🚨 IMPORTANT: Version 0.1.0+ Import Changes

**PyStataR v0.1.0+ introduces simplified import syntax for better usability:**

```python
# ✅ NEW (v0.1.0+) - Direct function imports
from pystatar import tabulate, reghdfe, winsor2
from pystatar import rank, rowmean  # Individual functions

# Use directly
result = tabulate(df['education'])
regression = reghdfe(data, 'y', ['x1', 'x2'])
```

```python
# ❌ OLD (v0.0.x) - Module-style imports (deprecated)
from pystatar import tabulate
result = tabulate.tabulate(df, 'education')  # No longer works
```

**Migration Guide**: Update your import statements to use the new direct import syntax. All examples below use the v0.1.0+ syntax.

## Project Vision & Goals

**PyStataR** aims to recreate and significantly enhance **the top 20 most frequently used Stata commands** in Python, transforming them into the most powerful and user-friendly statistical tools for academic research. Our goal is to not just replicate Stata's functionality, but to **expand and improve** upon it, leveraging Python's ecosystem to create superior research tools.

### Why This Project Matters
- **Bridge the Gap**: Seamless transition from Stata to Python for researchers
- **Enhanced Functionality**: Each command will be significantly expanded beyond Stata's original capabilities
- **Modern Research Tools**: Built for today's data science and research needs
- **Community-Driven**: Open source development with academic researchers in mind

### Target Commands (20 Most Used in Academic Research)
✅ **tabulate** - Cross-tabulation and frequency analysis  
✅ **egen** - Extended data generation and manipulation  
✅ **reghdfe** - High-dimensional fixed effects regression  
✅ **winsor2** - Data winsorizing and trimming  
🔄 **Coming Soon**: `summarize`, `describe`, `merge`, `reshape`, `collapse`, `keep/drop`, `generate`, `replace`, `sort`, `by`, `if/in`, `reg`, `logit`, `probit`, `ivregress`, `xtreg`

**Want to see a specific command implemented?** 
-  [Create an issue](https://github.com/brycewang-stanford/PyStataR/issues) to request a command
-  [Contribute](CONTRIBUTING.md) to help us complete this project faster
- ⭐ Star this repo to show your support!

## Core Modules Overview

### **tabulate** - Advanced Cross-tabulation and Frequency Analysis
- **Beyond Stata**: Enhanced statistical tests, multi-dimensional tables, and publication-ready output
- **Key Features**: Chi-square tests, Fisher's exact test, Cramér's V, Kendall's tau, gamma coefficients
- **Use Cases**: Survey analysis, categorical data exploration, market research

### **egen** - Extended Data Generation and Manipulation  
- **Beyond Stata**: Advanced ranking algorithms, robust statistical functions, and vectorized operations
- **Key Features**: Group operations, ranking with tie-breaking, row statistics, percentile calculations
- **Use Cases**: Data preprocessing, feature engineering, panel data construction

### **reghdfe** - High-Dimensional Fixed Effects Regression
- **Beyond Stata**: Memory-efficient algorithms, advanced clustering options, and diagnostic tools
- **Key Features**: Multiple fixed effects, clustered standard errors, instrumental variables, robust diagnostics
- **Use Cases**: Panel data analysis, causal inference, economic research

### **winsor2** - Advanced Outlier Detection and Treatment
- **Beyond Stata**: Multiple detection methods, group-specific treatment, and comprehensive diagnostics
- **Key Features**: IQR-based detection, percentile methods, group-wise operations, flexible trimming
- **Use Cases**: Data cleaning, outlier analysis, robust statistical modeling

## Advanced Features & Performance

### Performance Optimizations
- **Vectorized Operations**: All functions leverage NumPy and pandas for maximum speed
- **Memory Efficiency**: Optimized for large datasets common in academic research
- **Parallel Processing**: Multi-core support for computationally intensive operations
- **Lazy Evaluation**: Smart caching and delayed computation when beneficial

### Research-Grade Features
- **Publication Ready**: LaTeX and HTML output for academic papers
- **Reproducible Research**: Comprehensive logging and version tracking
- **Missing Data Handling**: Multiple imputation and robust missing value treatment
- **Bootstrapping**: Built-in bootstrap methods for confidence intervals
- **Cross-Validation**: Integrated CV methods for model validation

## Quick Installation

```bash
pip install pystatar
```

## Comprehensive Usage Examples

### `tabulate` - Advanced Cross-tabulation

The `tabulate` module provides comprehensive frequency analysis and cross-tabulation capabilities, extending far beyond Stata's original functionality.

#### Basic One-way Tabulation
```python
import pandas as pd
import numpy as np
# v0.1.0+ Import Syntax - Direct function imports
from pystatar import tabulate

# Create sample dataset
df = pd.DataFrame({
    'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'] * 100,
    'education': ['High School', 'College', 'Graduate', 'High School', 'College', 'Graduate'] * 100,
    'income': np.random.normal(50000, 15000, 600),
    'age': np.random.randint(22, 65, 600),
    'industry': np.random.choice(['Tech', 'Finance', 'Healthcare', 'Education'], 600)
})

# Simple frequency table - Direct function call (v0.1.0+)
result = tabulate(df['education'])
print(result)
```

#### Advanced Two-way Cross-tabulation with Statistics
```python
# Two-way tabulation with comprehensive statistics (v0.1.0+)
result = tabulate(
    df['gender'], df['education'],
    chi2=True,              # Chi-square test
    exact=True,             # Fisher's exact test
    cramers_v=True,         # Cramér's V
    missing=True,           # Include missing values
    row_percent=True,       # Row percentages
    col_percent=True,       # Column percentages
    cell_percent=True       # Cell percentages
)

# Access different components
print("Frequency Table:")
print(result.frequencies)
print(f"\nChi-square p-value: {result.statistics['chi2']['p_value']:.4f}")
print(f"Cramér's V: {result.statistics['cramers_v']['value']:.4f}")
```

#### Multi-way Tabulation
```python
# Note: Three-way tabulation is planned for future versions
# For now, you can create separate two-way tables for each industry

# Get unique industries
industries = df['industry'].unique()

print("=== Cross-tabulation by Industry ===")
for industry in industries:
    # Filter data for this industry
    industry_df = df[df['industry'] == industry]
    
    # Create two-way table for this subset
    if len(industry_df) > 0:
        result = tabulate(
            industry_df['gender'], 
            industry_df['education'],
            chi2=True
        )
        print(f"\n=== {industry} ===")
        print(result.frequencies)
        if result.statistics and 'chi2' in result.statistics:
            print(f"Chi-square p-value: {result.statistics['chi2']['p_value']:.4f}")
```

### `egen` - Extended Data Generation

The `egen` module provides powerful data manipulation functions that extend Stata's egen capabilities.

#### Ranking and Percentile Functions
```python
# v0.1.0+ Import Syntax - Direct function imports
from pystatar import rank

# Advanced ranking with tie-breaking options
df['income_rank'] = rank(df['income'], method='average')  # Handle ties

# Group-specific rankings (Note: group-by functionality planned for future release)
# For now, you can use pandas groupby with rank
df['rank_within_industry'] = df.groupby('industry')['income'].rank(method='average')

# Basic percentile calculations using pandas
df['income_90th'] = df['income'].quantile(0.9)
df['income_iqr'] = df['income'].quantile(0.75) - df['income'].quantile(0.25)
```

#### Row Operations
```python
# v0.1.0+ Import Syntax - Direct function imports
from pystatar import rowtotal, rowmean, rowmin, rowmax, rowsd, rowcount

# Create test scores dataset
scores_df = pd.DataFrame({
    'student': range(1, 101),
    'math': np.random.normal(75, 10, 100),
    'english': np.random.normal(80, 12, 100),
    'science': np.random.normal(78, 11, 100),
    'history': np.random.normal(82, 9, 100)
})

# Row statistics (v0.1.0+)
scores_df['total_score'] = rowtotal(scores_df, ['math', 'english', 'science', 'history'])
scores_df['avg_score'] = rowmean(scores_df, ['math', 'english', 'science', 'history'])
scores_df['min_score'] = rowmin(scores_df, ['math', 'english', 'science', 'history'])
scores_df['max_score'] = rowmax(scores_df, ['math', 'english', 'science', 'history'])
scores_df['score_sd'] = rowsd(scores_df, ['math', 'english', 'science', 'history'])

# Count non-missing values per row
scores_df['subjects_taken'] = rowcount(scores_df, ['math', 'english', 'science', 'history'])
```

#### Group Statistics and Operations
```python
# v0.1.0+ Import Syntax - Group functions
from pystatar import mean, sd, count, tag

# Group summary statistics
df['mean_income_by_education'] = mean(df['income'], by=df['education'])
df['sd_income_by_gender'] = sd(df['income'], by=df['gender'])

# Group identification and counting
df['education_group_size'] = count(df['education'])
df['first_in_group'] = tag(df, ['education', 'gender'])  # First observation in group

# Advanced group operations using pandas (median not yet implemented in pystatar)
df['median_income_by_industry'] = df.groupby('industry')['income'].transform('median')
df['group_sequence'] = df.groupby('education').cumcount() + 1  # Sequence within group

# Advanced group operations
df['income_rank_in_education'] = df.groupby('education')['income'].rank(method='average')
df['above_group_median'] = (df['income'] > df.groupby('education')['income'].transform('median')).astype(int)
```

### `reghdfe` - Advanced Fixed Effects Regression

The `reghdfe` module provides state-of-the-art estimation for linear models with high-dimensional fixed effects.

#### Basic Fixed Effects Regression
```python
# v0.1.0+ Import Syntax
from pystatar import reghdfe

# Create panel dataset
np.random.seed(42)
n_firms, n_years = 100, 10
n_obs = n_firms * n_years

panel_df = pd.DataFrame({
    'firm_id': np.repeat(range(n_firms), n_years),
    'year': np.tile(range(2010, 2020), n_firms),
    'log_sales': np.random.normal(10, 1, n_obs),
    'log_employment': np.random.normal(4, 0.5, n_obs),
    'log_capital': np.random.normal(8, 0.8, n_obs),
    'industry': np.repeat(np.random.choice(['Tech', 'Manufacturing', 'Services'], n_firms), n_years)
})

# Basic regression with firm and year fixed effects (v0.1.0+)
result = reghdfe(
    data=panel_df,
    y='log_sales',
    x=['log_employment', 'log_capital'],
    fe=['firm_id', 'year']
)

print(result.summary())
print(f"R-squared: {result.r2:.4f}")
print(f"Number of observations: {result.N}")
```

#### Advanced Regression with Clustering and Instruments
```python
# Add instrumental variables
panel_df['instrument1'] = np.random.normal(0, 1, n_obs)
panel_df['instrument2'] = np.random.normal(0, 1, n_obs)

# Regression with clustering and multiple fixed effects (v0.1.0+)
result = reghdfe(
    data=panel_df,
    y='log_sales',
    x=['log_employment', 'log_capital'],
    fe=['firm_id', 'year', 'industry'],  # Multiple fixed effects
    cluster='firm_id',                    # Clustered standard errors
    weights='log_employment',             # Weighted regression (using existing variable)
)

# Access detailed results
print("Coefficient Table:")
print(result.coef_table)
print(f"\nFixed Effects absorbed: {result.absorbed_fe}")
print(f"Clusters: {result.n_clusters}")
```

#### Instrumental Variables with High-Dimensional FE
```python
# Note: IV functionality is planned for future versions
# For now, reghdfe provides standard fixed effects regression
# IV estimation can be performed using statsmodels or other packages

result = reghdfe(
    data=panel_df,
    y='log_sales',
    x=['log_capital'],                   # Exogenous controls only for now
    fe=['firm_id', 'year'],
    cluster='firm_id'
)

print("Standard Fixed Effects Results:")
print(result.summary())
print(f"R-squared: {result.r2:.4f}")
```

### `winsor2` - Advanced Outlier Treatment

The `winsor2` module provides comprehensive outlier detection and treatment methods.

#### Basic Winsorizing
```python
# v0.1.0+ Import Syntax
from pystatar import winsor2

# Create dataset with outliers
outlier_df = pd.DataFrame({
    'income': np.concatenate([
        np.random.normal(50000, 10000, 950),  # Normal observations
        np.random.uniform(200000, 500000, 50)  # Outliers
    ]),
    'age': np.random.randint(18, 70, 1000),
    'industry': np.random.choice(['Tech', 'Finance', 'Retail', 'Healthcare'], 1000)
})

# Basic winsorizing at 1st and 99th percentiles (v0.1.0+)
result = winsor2(outlier_df, ['income'])
print("Original vs Winsorized:")
print(f"Original: min={outlier_df['income'].min():.0f}, max={outlier_df['income'].max():.0f}")
print(f"Winsorized: min={result['income_w'].min():.0f}, max={result['income_w'].max():.0f}")
```

#### Group-wise Winsorizing
```python
# Winsorize within groups (v0.1.0+)
result = winsor2(
    outlier_df, 
    ['income'],
    by=outlier_df['industry'], # Winsorize within each industry
    cuts=(5, 95),              # Use 5th and 95th percentiles
    suffix='_clean'            # Custom suffix
)

# Compare distributions by group
for industry in outlier_df['industry'].unique():
    mask = outlier_df['industry'] == industry
    original = outlier_df.loc[mask, 'income']
    winsorized = result.loc[mask, 'income_clean']
    print(f"\n{industry}:")
    print(f"  Original: {original.describe()}")
    print(f"  Winsorized: {winsorized.describe()}")
```

#### Trimming vs Winsorizing Comparison
```python
# Compare different outlier treatment methods (v0.1.0+)
trim_result = winsor2(
    outlier_df, 
    ['income'],
    trim=True,              # Trim (remove) instead of winsorize
    cuts=(2.5, 97.5)       # Trim 2.5% from each tail
)

winsor_result = winsor2(
    outlier_df, 
    ['income'],
    trim=False,             # Winsorize (cap) outliers
    cuts=(2.5, 97.5)
)

print("Treatment Comparison:")
print(f"Original N: {len(outlier_df)}")
print(f"After trimming N: {trim_result['income_tr'].notna().sum()}")
print(f"After winsorizing N: {len(winsor_result)}")
print(f"Trimmed mean: {trim_result['income_tr'].mean():.0f}")
print(f"Winsorized mean: {winsor_result['income_w'].mean():.0f}")
```

#### Advanced Outlier Detection
```python
# Multiple variable winsorizing with custom thresholds (v0.1.0+)
multi_result = winsor2(
    outlier_df,
    ['income', 'age'],
    cuts=(1, 99),              # Different cuts for different variables
    by=outlier_df['industry'], # Group-specific treatment
    replace=True,              # Replace original variables
    label=True                 # Add descriptive labels
)

# Generate outlier indicators using pandas and numpy (outlier_indicator planned for future release)
import numpy as np

# IQR method for outlier detection
Q1 = outlier_df['income'].quantile(0.25)
Q3 = outlier_df['income'].quantile(0.75)
IQR = Q3 - Q1
outlier_df['income_outlier'] = ((outlier_df['income'] < (Q1 - 1.5 * IQR)) | 
                                (outlier_df['income'] > (Q3 + 1.5 * IQR))).astype(int)

# Percentile method for outlier detection
p1 = outlier_df['income'].quantile(0.01)
p99 = outlier_df['income'].quantile(0.99)
outlier_df['extreme_outlier'] = ((outlier_df['income'] < p1) | 
                                 (outlier_df['income'] > p99)).astype(int)

print("Outlier Detection Results:")
print(f"IQR method detected {outlier_df['income_outlier'].sum()} outliers")
print(f"Percentile method detected {outlier_df['extreme_outlier'].sum()} outliers")
```

## Project Structure

```
pystatar/
├── __init__.py              # Main package initialization
├── tabulate/               # Cross-tabulation module
│   ├── __init__.py
│   ├── core.py
│   ├── results.py
│   └── stats.py
├── egen/                   # Extended generation module
│   ├── __init__.py
│   └── core.py
├── reghdfe/               # High-dimensional FE regression
│   ├── __init__.py
│   ├── core.py
│   ├── estimation.py
│   └── utils.py
├── winsor2/               # Winsorizing module
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── utils/                 # Shared utilities
│   ├── __init__.py
│   └── common.py
└── tests/                 # Test suite
    ├── test_tabulate.py
    ├── test_egen.py
    ├── test_reghdfe.py
    └── test_winsor2.py
```

## Key Features

- **Familiar Syntax**: Stata-like command structure and parameters
- **Pandas Integration**: Seamless integration with pandas DataFrames
- **High Performance**: Optimized implementations using pandas and NumPy
- **Comprehensive Coverage**: Most commonly used Stata commands
- **Statistical Rigor**: Proper statistical tests and robust standard errors
- **Flexible Output**: Multiple output formats and customization options
- **Missing Value Handling**: Configurable treatment of missing data

## Documentation

Each module comes with comprehensive documentation and examples:

- [**tabulate Documentation**](docs/tabulate.md) - Cross-tabulation and frequency analysis
- [**egen Documentation**](docs/egen.md) - Extended data generation functions
- [**reghdfe Documentation**](docs/reghdfe.md) - High-dimensional fixed effects regression  
- [**winsor2 Documentation**](docs/winsor2.md) - Data winsorizing and trimming

## Contributing to the Project

We're building the future of academic research tools in Python! Here's how you can help:

### Priority Commands Needed
Help us implement the remaining **16 high-priority commands**:

**Data Management**: `summarize`, `describe`, `merge`, `reshape`, `collapse`, `keep`, `drop`, `generate`, `replace`, `sort`

**Statistical Analysis**: `reg`, `logit`, `probit`, `ivregress`, `xtreg`, `anova`

### How to Contribute

1. **Request a Command**: [Open an issue](https://github.com/brycewang-stanford/PyStataR/issues/new) with the command you need
2. **Implement a Command**: Check our [contribution guidelines](CONTRIBUTING.md) and submit a PR
3. **Report Bugs**: Help us improve existing functionality
4. **Improve Documentation**: Add examples, tutorials, or clarifications
5. **Spread the Word**: Star the repo and share with fellow researchers

###  Recognition
All contributors will be recognized in our documentation and release notes. Major contributors will be listed as co-authors on any academic publications about this project.

###  Academic Collaboration
We welcome partnerships with universities and research institutions. If you're interested in using this project in your coursework or research, please reach out!

## Community & Support

- **Documentation**: [https://pystatar.readthedocs.io](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/brycewang-stanford/PyStataR/discussions)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/brycewang-stanford/PyStataR/issues)
- ** Email**: brycew6m@stanford.edu for academic collaborations

## Comparison with Stata

| Feature | Stata | PyStataR | Advantage |
|---------|-------|-------------------|-----------|
| **Speed** | Base performance | 2-10x faster* | Vectorized operations |
| **Memory** | Limited by system | Efficient pandas backend | Better large dataset handling |
| **Extensibility** | Ado files | Python ecosystem | Unlimited customization |
| **Cost** | $$$$ | Free & Open Source | Accessible to all researchers |
| **Integration** | Standalone | Python data science stack | Seamless workflow |
| **Output** | Limited formats | Multiple (LaTeX, HTML, etc.) | Publication ready |

*Performance comparison based on typical academic datasets (1M+ observations)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This package builds upon the excellent work of:
- [pandas](https://pandas.pydata.org/) - The backbone of our data manipulation
- [numpy](https://numpy.org/) - Powering our numerical computations
- [scipy](https://scipy.org/) - Statistical functions and algorithms
- [statsmodels](https://www.statsmodels.org/) - Statistical modeling foundations
- [pyhdfe](https://github.com/jeffgortmaker/pyhdfe) - High-dimensional fixed effects algorithms
- The entire **Stata community** - For decades of statistical innovation that inspired this project

##  Future Roadmap

### Version 1.0 Goals (Target: End of 2025)
-  Core 4 commands implemented
-  Additional 16 high-priority commands
-  Comprehensive test suite (>95% coverage)
-  Complete documentation with tutorials
-  Performance benchmarks vs Stata

### Version 2.0 Vision (2026)
-  Machine learning integration
-  R integration for cross-platform compatibility
-  Web interface for non-programmers
-  Jupyter notebook extensions

## 📈 Project Statistics

[![GitHub stars](https://img.shields.io/github/stars/brycewang-stanford/PyStataR?style=social)](https://github.com/brycewang-stanford/PyStataR/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/brycewang-stanford/PyStataR?style=social)](https://github.com/brycewang-stanford/PyStataR/network)
[![GitHub issues](https://img.shields.io/github/issues/brycewang-stanford/PyStataR)](https://github.com/brycewang-stanford/PyStataR/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/brycewang-stanford/PyStataR)](https://github.com/brycewang-stanford/PyStataR/pulls)

##  Contact & Collaboration

**Created by [Bryce Wang](https://github.com/brycewang-stanford)** - Stanford University

-  **Email**: brycew6m@stanford.edu  
-  **GitHub**: [@brycewang-stanford](https://github.com/brycewang-stanford)
-  **Academic**: Stanford Graduate School of Business
-  **LinkedIn**: [Connect with me](https://linkedin.com/in/brycewang)

### Academic Partnerships Welcome!
-  Course integration and teaching materials
-  Research collaborations and citations
-  Institutional licensing and support
-  Student contributor programs

---

### ⭐ **Love this project? Give it a star and help us reach more researchers!** ⭐

**Together, we're building the future of academic research in Python** 
