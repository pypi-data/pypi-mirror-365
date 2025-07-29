from setuptools import setup, find_packages

setup(
    name='easekit',
    version='1.0.0',
    author='Srishti Gupta',
    author_email='srishtig253@gmail.com',
    description='A metric to evaluate empathy in dialogue systems',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/srishtigupta253/easekit',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'torch',
        'transformers',
        'scikit-learn',
        'nltk',
        'vaderSentiment'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
