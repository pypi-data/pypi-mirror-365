from setuptools import setup, find_packages

# ✅ Read long description using UTF-8
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="licome",
    version="2.0.0",
    author="Rohit Kumar Behera",
    author_email="rohitmbl24@gmail.com",
    description="Linear Congruential Method (LCM) pseudo-random number generator",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for PyPI formatting
    url="https://github.com/yourusername/licome",   # Optional: your GitHub repo
    packages=find_packages(),
    install_requires=["numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)
