from setuptools import setup

setup(name='r53ddns',
      version='1.0',
      description='OpenShift App',
      author='Lars Kellogg-Stedman',
      author_email='lars@oddbit.com',
      install_requires = open('requirements.txt').readlines(),
      url='http://www.python.org/sigs/distutils-sig/',
#      install_requires=['Django>=1.3'],
     )

