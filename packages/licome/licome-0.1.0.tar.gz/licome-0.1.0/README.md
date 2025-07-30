# LICOME

**LICOME** (Linear Congruential Method) is a simple Python package to generate pseudo-random numbers using the Linear Congruential Method (LCM) algorithm.

It provides both the raw generated numbers and their normalized versions between [0, 1).

---

## 🔧 Features

- Simple to use
- Fast LCM-based random number generator
- Normalized output using NumPy
- Accepts user-defined parameters for full control

---

## 📦 Installation

Once this package is uploaded to PyPI, it can be installed using:

```bash
pip install licome


you can directly install from your GitHub repo:

pip install git+https://github.com/muinrohit/licome.git


🚀USAGE
`````````

from licome import LICOME

# Parameters:
# a     = multiplier
# c     = increment
# x0    = seed value (initial value)
# m     = modulus
# count = how many numbers to generate

y, u = LICOME(a=2, c=3, x0=5, m=103, count=10)

print("Generated:", y)
print("Normalized:", u)

📄 Function Details
````````````````````
def LICOME(a: int, c: int, x0: int, m: int, count: int):
    """
    Linear Congruential Method (LCM) to generate pseudo-random numbers.

    Parameters:
        a (int): Multiplier
        c (int): Increment
        x0 (int): Seed value (initial value)
        m (int): Modulus
        count (int): Number of pseudo-random numbers to generate

    Returns:
        tuple: A tuple (y, u)
            y (list): Generated sequence of integers
            u (ndarray): Normalized values in [0, 1)
    """

🧪 How to Run the Example
```````````````````````````
If you're developing and testing locally, create a main.py file in the project folder:

python
Copy
Edit
from licome import LICOME

def main():
    y, u = LICOME(2, 3, 5, 103, 10)
    print("Generated:", y)
    print("Normalized:", u)

if __name__ == "__main__":
    main()


👤 Author
```````````
Developed by Rohit Kumar Behera
Email: rohitmbl24@gmail.com


📜 License
```````````
This project is licensed under the MIT License – see the LICENSE file for details.

yaml
Copy
Edit

---

## ✅ After This

You now have:
- `setup.py` — for packaging
- `__init__.py` — contains your function
- `LICENSE` — open source license
- `README.md` — clear usage and description
- `main.py` — test file

You're now **ready to build and upload to PyPI!**

---

## ❓ Next Steps You Can Do:

1. Build your package:
   ```bash
   python -m build

