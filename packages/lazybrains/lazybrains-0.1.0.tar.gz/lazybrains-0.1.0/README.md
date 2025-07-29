# lazybrains

**lazybrains** is a simple model selection tool for linear regression, supporting OLS (Normal Equation), Batch Gradient Descent (BGD), and BGD with L1 regularization (Lasso). It is built on top of pandas and numpy.


## Usage

### 1. Import and Prepare Data

```python
import pandas as pd
from lazybrains import Lazy_Work

df = pd.read_csv("your_data.csv")
lm = Lazy_Work(df)
```

### 2. Split Data

```python
lm.fit_data(
    random_state=42,
    ratio=0.8,
    training_features=['feature1', 'feature2'],
    target_features=['target']
)
```

### 3. Standardize Features (Optional)

```python
lm.Standard_Scale(features=['feature1', 'feature2'])
```

### 4. Train Models

#### OLS (Normal Equation)

```python
score = lm.doML(model="lr", method="ols", get_equation=True)
print("R2 Score:", score)
```

#### Batch Gradient Descent

```python
score = lm.doML(model="lr", method="bgd", epochs=200, learning_rate=0.01, get_equation=True)
print("R2 Score:", score)
```

#### Lasso Regression (BGD + L1)

```python
score = lm.doML(model="lr", method="bgd", penalty="l1", epochs=200, learning_rate=0.01, lamda_=0.1, get_equation=True)
print("R2 Score:", score)
```

### 5. Save/Load Model

```python
lm.save_model(model_obj, filename="model.pkl")
loaded_model = lm.load_model(filename="model.pkl")
```

---

MIT

---

