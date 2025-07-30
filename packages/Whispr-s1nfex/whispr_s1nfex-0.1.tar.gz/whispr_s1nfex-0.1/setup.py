from setuptools import setup, find_packages

setup(
    name='Whispr-s1nfex',            # tavo PyPI pavadinimas (turi būti unikalus)
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    author='S1nfex',
    author_email='rirbd70@gmail.com',
    description='S1nfex package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://example.com',         # neprivaloma
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
