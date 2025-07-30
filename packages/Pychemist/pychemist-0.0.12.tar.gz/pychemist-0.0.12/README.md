# Pychemist

The Alchemist of Data Science

**Transform raw data into insights.**

Pychemist is a lightweight Python library designed to simplify and enrich your data science workflow. Inspired by the transformation mindset of an alchemist, it helps you turn raw data into golden insights. Pychemist replaces complex, repetitive code with a clean and intuitive syntax that streamlines data cleaning, transformation, and preparation to reveal clear insights. It also enables clean and well-structured presentation of results, making it easier to communicate findings effectively.

---

## Features

- Create lagged or lead variables for time-series and panel data
- Run quick, readable t-tests on treatment groups
- Filter model summaries to hide fixed effects
- Conditional mutation of DataFrames
- Pandas accessor (`.chem`) for fluent, chainable workflows

## Installation

```bash
pip install pychemist
```

## Usage
```python
import pychemist as chem
```

# Example 1: Conditional mutation using the `df.chem.mutate` DataFrame accessor.

Update the `total_assets` for a specific company and year to a given value:

```python
df=df.chem.mutate('company_id == "8ga62sav" & year==2025', "total_assets", 82000000)
```

# Example 2: Conditional mutation using the `df.chem.mutate` DataFrame accessor.

Set the `Promotion` column to `1` for managers who haven't been promoted in `3` or more `years` and have a performance rating of at least `4`; otherwise set it to `0`.

```python
df = df.chem.mutate('YearsSinceLastPromotion >= 3 & JobRole == "Manager" & PerformanceRating >= 4', 'Promotion', 1, 0)
```

# Example 3: Creating lagged variables using the `df.chem.lag` DataFrame accessor.

Create lagged versions of `total assets` and `net income` for each `ticker`, only when the `year` difference is exactly `1`:

```python
df=df.chem.lag(['total assets','net income'],'ticker','year')
```

# Example 4: Creating leading variables using the `df.chem.lead` DataFrame accessor.

Create lead (future) versions of `total assets` and `net income` for each `ticker`, only when the `year` difference is exactly `1`:

```python
df=df.chem.lead(['total assets','net income'],'ticker','year')
```

# Example 5: Creating 2-year lagged variables using the `df.chem.lag` DataFrame accessor.

Create lagged versions of `total assets` and `net income` for each `ticker`, only when the `year` difference is exactly `2`:

```python
df=df.chem.lag(['total assets','net income'],'ticker','year',2)
```

# Example 6: T-test between treated and control groups
```python
chem.ttest(df, variable="outcome", treatment="treated")
```

# Example 7: Model summary without fixed effects
```python
import statsmodels.formula.api as smf
model = smf.ols("y ~ x + C(firm)", data=df).fit()
print(chem.summary_no_fe(model))
```


MIT License
Copyright (c) Jeroen van Raak (2025)