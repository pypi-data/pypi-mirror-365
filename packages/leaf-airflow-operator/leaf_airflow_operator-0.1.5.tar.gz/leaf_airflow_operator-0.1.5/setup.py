from setuptools import setup, find_packages

setup(
    name='leaf-airflow-operator',
    version='0.1.5',
    description='Custom Apache Airflow operator to interact with Leaf Agriculture API',
    author='Luiz Henrique Zambom Santana',
    packages=find_packages(),
    install_requires=[
        'apache-airflow>=2.4.0',
        'requests>=2.25.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ]
)
