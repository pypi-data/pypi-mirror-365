from setuptools import setup, find_packages

setup(
    name='mugem',
    version='3.0',
    description='Multiplicative Generative Method (MGM)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Rohit Kumar Behera',
    author_email='rohitmbl24@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)