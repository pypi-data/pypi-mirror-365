from setuptools import setup, find_packages

setup(
    name='pynometry',
    version='0.1.0',
    description='A collection of Math functions',
    author='Unknown',
    packages=find_packages(),
    include_package_data=True,  
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
