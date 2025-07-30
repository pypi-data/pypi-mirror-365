# Mugem

**Mugem (Multiplicative Generative Method)** is a lightweight Python package that generates pseudo-random numbers using the **Multiplicative Congruential Method (MCM)**. it is widely used random number generation algorithm defined by the recurrence relation:

It returns both the raw sequence of generated numbers and their normalized versions between `[0, 1)` using NumPy.

---

## Features

- Easy-to-use function interface  
- Pure Multiplicative Congruential Method (no increment term)  
- Fast random number generation  
- Normalized output with NumPy  
- User-defined input parameters  

---


## Installation

Install via pip:

```bash
pip install mugem
```

> *(Use after publishing to PyPI)*

---

## Usage

```python
from mugem import mgm

# Define parameters
a = 2        # Multiplier
x0 = 5       # Seed value
m = 103      # Modulus
count = 10   # Number of values

# Generate pseudo-random numbers
y, u = mgm(a, x0, m, count)

print("Generated:", y)
print("Normalized:", u)
```

---

## Function Reference

```python
def mgm(a: int, x0: int, m: int, count: int = 10):
    """
    Multiplicative Congruential Method (MCM) to generate pseudo-random numbers.

    Parameters:
        a (int): Multiplier
        x0 (int): Initial seed value
        m (int): Modulus
        count (int): Total numbers to generate

    Returns:
        tuple:
            y (list): Raw generated integers
            u (ndarray): Normalized values in [0, 1)
    """
```

---

## Example Script

```python
from mugem import mgm

a, x0, m, count = 2, 5, 103, 10
y, u = mgm(a, x0, m, count)

print("Generated Sequence:", y)
print("Normalized Sequence:", u)
```

---

## Author

**Rohit Kumar Behera**

📧 Email: rohitmbl24@gmail.com 

PyPI: [https://pypi.org/project/mgm/] 

---
Feel free to contribute, suggest improvements, or report issues.
