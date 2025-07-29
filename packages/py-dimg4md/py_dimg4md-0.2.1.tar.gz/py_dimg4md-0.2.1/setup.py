from setuptools import setup, find_packages

setup(
    name="py-dimg4md", 
    version="0.2.1",  # Updated version number
    packages=find_packages(),
    readme="README.md",
    install_requires=[
        "requests>=2.28.2",
        "click>=8.0.0",
    ],
    extras_require={
        "picgo": [
            # Node.js and PicGo CLI are required for upload functionality
            # These need to be installed separately via npm:
            # npm install -g picgo
        ]
    },
    entry_points={
        'console_scripts': [
            'dimg = dimg4md.cli:cli',
        ]
    },
)