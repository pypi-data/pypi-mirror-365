from setuptools import setup, find_packages

setup(
    name='canada-testgen',
    version='0.1.1',
    description='Generate realistic Canadian test data from schema',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jeremie Nombro',
    author_email='guillaumenombro@gmail.com',
    url='https://github.com/your-username/canada-testgen',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'faker',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'canada-testgen=canada_testgen.cli:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
