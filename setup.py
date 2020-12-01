# @Author: gadal
# @Date:   2020-12-01T12:00:30+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2020-12-01T13:05:17+01:00

from setuptools import setup, find_packages

setup(name='Wind_data',
      version='0.1',
      # description='The funniest joke in the world',
      # url='http://github.com/storborg/funniest',
      # dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0'],
      long_description=__doc__,
      author='Cyril Gadal',
      author_email='gadal@ipgp.fr',
      include_package_data=True,
      license='GNU',
      packages=find_packages(),
      package_data={'Wind_data': ['src/*.kml']},
      zip_safe=False,
      python_requires='>=3',
      install_requires=[
        "numpy", "matplotlib", "cdsapi", "os", "itertools", "decimal", "scipy", "datetime", "windrose", "functools",
    ])
