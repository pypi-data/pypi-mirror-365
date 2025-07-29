from setuptools import setup, find_packages

setup(
    name='sf_label_skew',
    version='0.1.0',
    description='Same Features, Different Label Skew Generator using KMeans and Davies-Bouldin',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'scikit-learn',
    ],
    python_requires='>=3.6',
)
