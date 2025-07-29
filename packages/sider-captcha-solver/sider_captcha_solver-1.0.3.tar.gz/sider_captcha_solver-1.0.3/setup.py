# -*- coding: utf-8 -*-
"""
Setup script for Sider_CAPTCHA_Solver
"""
import os
from setuptools import setup, find_packages

# Read the README file
def read_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='sider-captcha-solver',
    version='1.0.3',
    author='TomokotoKiyoshi',
    author_email='',  # Add your email if you want
    description='Industrial-grade slider CAPTCHA recognition system based on deep learning',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/TomokotoKiyoshi/Sider_CAPTCHA_Solver',
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'sider_captcha_solver': 'src'},
    py_modules=['sider_captcha_solver'],
    include_package_data=True,
    package_data={
        'sider_captcha_solver': [
            'checkpoints/*/best_model.pth',
        ],
    },
    install_requires=read_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='captcha slider recognition deep-learning pytorch centernet',
    python_requires='>=3.8',
    project_urls={
        'Bug Reports': 'https://github.com/TomokotoKiyoshi/Sider_CAPTCHA_Solver/issues',
        'Source': 'https://github.com/TomokotoKiyoshi/Sider_CAPTCHA_Solver',
        'Documentation': 'https://github.com/TomokotoKiyoshi/Sider_CAPTCHA_Solver/blob/main/README.md',
    },
)