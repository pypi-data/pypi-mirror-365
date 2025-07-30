# LICOME

**LICOME (Linear Congruential Method)** is a lightweight Python package that generates pseudo-random numbers using the Linear Congruential Method (LCM).

It returns both the raw sequence of generated numbers and their normalized versions between `[0, 1)` using NumPy.

---

## 🔧 Features

- Simple and clean API  
- Fast LCM-based random number generation  
- Normalized output with NumPy  
- User-defined input parameters  

---

## 📦 Installation

Install via pip:

```bash
pip install licome
```

---

## 🚀 Usage

```python
from licome import LICOME

# Define parameters
a = 2        # Multiplier
c = 3        # Increment
x0 = 5       # Seed value
m = 103      # Modulus
count = 10   # Number of values

# Generate pseudo-random numbers
y, u = LCM(a, c, x0, m, count)

print("Generated:", y)
print("Normalized:", u)
```

---

## 📄 Function Reference

```python
def LCM(a: int, c: int, x0: int, m: int, count: int):
    """
    Linear Congruential Method to generate pseudo-random numbers.

    Parameters:
        a (int): Multiplier
        c (int): Increment
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

## 🧪 Example Script

```python
from licome import LCM  # Make sure this matches the folder name!

a, c, x0, m, count = 2, 3, 5, 103, 10
y, u = LCM(a, c, x0, m, count)
print("Generated Sequence:", y)
print("Normalized Sequence:", u)

```

---

## 👤 Author

**Rohit Kumar Behera**  
---

*Feel free to contribute, suggest improvements, or report issues.*
=======
📧 Email: [rohitmbl24@gmail.com]
(mailto:rohitmbl24@gmail.com)  
🔗 PyPI: [https://pypi.org/project/licome/]

---
