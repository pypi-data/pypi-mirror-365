from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='tcai-pay-x',
    version='0.1.0',
    description='A Flask-based web app for matching invoices to purchase orders using OCR and fuzzy matching.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='The Celeritas AI',
    author_email='business@theceleritasai.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==3.1.1",
        "numpy==2.2.6",
        "pandas==2.2.3",
        "openpyxl==3.1.5",
        "pytesseract==0.3.13",
        "pdf2image==1.17.0",
        "pillow==11.2.1",
        "RapidFuzz==3.13.0",
        "python-dateutil==2.9.0.post0",
        "packaging==25.0"
    ],
    entry_points={
        'console_scripts': [
            'tcai-pay-x=tcai_pay_x.webapp:run_app',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
