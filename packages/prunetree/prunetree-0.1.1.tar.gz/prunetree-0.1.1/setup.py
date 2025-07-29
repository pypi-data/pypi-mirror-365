from setuptools import setup, find_packages

setup(
    name='prunetree',
    version='0.1.1',
    description='A DecisionTreeClassifier with automatic validation-based pruning',
    author='Arun Sundar',
    author_email='karthicksundar2001@gmail.com',
    packages=find_packages(),
    install_requires=[
        'scikit-learn>=1.0',
        'numpy>=1.20',
    ],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
