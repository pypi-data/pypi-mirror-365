from setuptools import setup, find_packages

setup(
    name='RFmodule',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['numpy','pandas','matplotlib','seaborn','scikit-learn','joblib','scipy'],
    description='A collection of useful Python functions to create finely tuned classification and regression models',
    author='Soukaina Timouma',
    author_email='soukaina.timouma@ox.ac.uk',
    license='MIT',
)
