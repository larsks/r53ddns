from setuptools import setup, find_packages

with open('requirements.txt') as fd:
    requirements = fd.readlines()

setup(name='r53ddns',
      version='1.0',
      description='AWS Route53 Dynamic DNS Service',
      author='Lars Kellogg-Stedman',
      author_email='lars@oddbit.com',
      packages=find_packages(),
      install_requires=requirements,
      url='http://github.com/larsks/r53ddns/',
      )
