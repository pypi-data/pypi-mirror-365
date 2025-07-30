import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HackKit",
    version="1.0.0",
    author="Mohammad Taha Gorji",
    author_email="MohammadTahaGorjiProfile@gmail.com",
    description="WiFi, CSRF, LFI/RFI, SSTI, XXE, SSRF, file uploads, directory brute‑force, auth bypass, header analysis, WordPress exploitation, and more. Missing any method is unacceptable — every function below is exhaustively documented with descriptions, parameters, return values, example usage, and a master example for each class demonstrating all capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)