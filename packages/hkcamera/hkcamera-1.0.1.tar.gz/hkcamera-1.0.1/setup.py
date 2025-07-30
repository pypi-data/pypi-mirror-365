from setuptools import setup, find_packages
import os

# Read the contents of MANIFEST.in
manifest_path = os.path.join(os.path.dirname(__file__), 'MANIFEST.in')
if os.path.exists(manifest_path):
    with open(manifest_path, 'r') as f:
        manifest_lines = f.readlines()
else:
    manifest_lines = []

setup(
    name='hkcamera',
    version='1.0.1',
    description='A package for Hikvision camera integration',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'opencv-python',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)