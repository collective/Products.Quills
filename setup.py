from setuptools import setup, find_packages
import os

version = '1.7.0'

setup(name='Products.Quills',
      version=version,
      description="A Blogging Product for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone blogging',
      author='Quills Team',
      author_email='plone-quills@googlegroups.com',
      url='http://plone.org/products/quills',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'quills.app',
          'Products.basesyndication',
          'Products.fatsyndication',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
