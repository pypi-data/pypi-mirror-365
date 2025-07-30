from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hprocess',
    version='1.0.1',
    description='Process management and monitoring library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    package_dir={'hprocess': 'hprocess'},
    package_data={"hprocess": ["**"]},
    include_package_data=True,
    install_requires=[
        "psutil"
    ],
    python_requires='>=3.7',
    license="MIT",
)