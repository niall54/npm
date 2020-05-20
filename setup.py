from setuptools import setup

setup(
  name='npm',
  version='0.1.2',
  author='Niall Moroney',
  author_email='niall_moroney@hotmail.co.uk',
  packages=['npm'],
  url='https://github.com/niall54/npm',
  license='LICENSE.txt',
  description='An awesome package that does something',
  long_description=open('README.txt').read(),
  install_requires=[
      "numpy",
      "matplotlib",
  ],
)
