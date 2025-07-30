from setuptools import setup, find_packages

setup(
    name="ascpy",
    version="0.1.0",
    description="Reusable Python utility library for all my projects",
    author="Backup Squre",
    author_email="backup@example.com",
    license="MIT",
    license_files=[],
    packages=find_packages(),
    python_requires=">=3.8",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/navdeepChad/pyPItest",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    include_package_data=True,
)
