from setuptools import setup, find_packages

setup(
    name="pralekh",
    version="0.1.0",
    description="Unified document text and table extractor for PDFs, DOCX, PPTX, XLSX, and TXT (with OCR support)",
    author="Jasteg Singh",
    author_email="jastegsingh007@gmail.com",
    url="https://github.com/JastegSingh19/pralekh",
    packages=find_packages(),
    install_requires=[
        "pdfplumber",
        "pytesseract",
        "python-docx",
        "python-pptx",
        "pandas",
        "Pillow"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
