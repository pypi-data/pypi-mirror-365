from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="skorkart",
    version="0.1.0",
    packages=find_packages(),
    author="Uraz Akgül",
    author_email="urazdev@gmail.com",
    description="Fetches financial scorecard tables for BIST stocks from Halk Yatırım portal.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/urazakgul/skorkart",
    license="MIT",
    install_requires=[
        "pandas",
        "selenium",
        "lxml",
        "webdriver-manager",
        "openpyxl"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.9",
)