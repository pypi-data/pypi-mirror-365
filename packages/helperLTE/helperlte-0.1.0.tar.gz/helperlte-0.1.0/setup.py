from setuptools import setup, find_packages

setup(
    name='helperLTE', # PIP-də görünəcək kitabxananızın adı
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'torch>=1.8.0', 
        'torchvision>=0.9.0',
        'tqdm',
    ],
    author='bahramzada', 
    author_email='raulbahramzada@gmail.com', 
    description='This is a utility library for ML tasks including image processing and model training.',
    long_description=open('README.md', encoding='utf-8').read(),    long_description_content_type='text/markdown',
    url='https://github.com/bahramzada/helperfunctions', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8', 
)
