from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hyyshare',
    version='2025.7.27',
    description='hyyshare',
    long_description=long_description,
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    package_dir={'hyyshare': 'hyyshare'},
    package_data={"hyyshare": ["**"]},
    include_package_data=True,
    install_requires=[
        'pywin32',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "hyyshare = hyyshare.cli:main"
        ]
    },
)