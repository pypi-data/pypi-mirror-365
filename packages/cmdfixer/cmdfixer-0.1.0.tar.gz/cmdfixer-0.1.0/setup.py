from setuptools import setup, find_packages

setup(
    name='cmdfixer',
    version='0.1.0',
    description='Suggests corrections for mistyped CLI commands (git, Linux, Kubernetes, etc.)',
    author='Nikhil Kumar',
    author_email='kumarn7570@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cmdfixer=fix_cmd.cli:main',
        ],
    },
    python_requires='>=3.6',
    install_requires=['thefuzz'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
