from setuptools import setup, find_packages

setup(
  name = "AMFTools",
  version = "0.1.9",
  author="Advanced_Microfluidics_SA",
  author_email="info@amf.ch",
  license='proprietary license (Advanced Microfluidics SA)',
  license_files=('licence',),
  description='AMF Tools is a python package to control Advanced Microfluics SA devices',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  url='https://amf.ch',
  packages=find_packages(exclude=["testing"]),
  install_requires=[
    'pyserial',
    'ftd2xx',
  ],
  python_requires='>=3.8',
  classifiers=[
    "Programming Language :: Python :: 3",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3.11",
    "Topic :: Security"
  ],
)