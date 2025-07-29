from setuptools import setup, find_packages

setup(
    name="pdf_translator_package",
    version="0.1.1",
    description="Application Django pour traduire des fichiers PDF",
    author="Lou Christelle",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.2",
        "PyPDF2",
        "fpdf",
        "googletrans==4.0.0-rc1"
    ],
)
