from setuptools import setup, find_packages

setup(
    name='vaultsphere',
    version='1.0.1',
    description='VaultSphere - A simple encrypted NoSQL-like database with base64 encoding.',
    author='zzzNeet',
    # author_email='',
    packages=find_packages(),
    install_requires=[
        'cryptography>=41.0.0'
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'vaultsphere=vaultsphere.cli:main',
            "vs=vaultsphere.cli:main",
        ],
    },
)
