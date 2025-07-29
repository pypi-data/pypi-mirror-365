from setuptools import setup, find_packages

setup(
    name='easypythonx',
    version='0.1.0',
    author='Tristan',
    author_email='likelikefootball@gmail.com',
    description='A simple wrapper around boto3, requests, urllib3, and pyinstaller for fast automation.',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'requests',
        'urllib3',
        'pyinstaller'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
