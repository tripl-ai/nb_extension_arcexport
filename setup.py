from setuptools import setup

setup(name='ArcExporter',
      version='0.0.3',
      description='Export Jupyter notebook as Arc .json file',
      author='Mike Seddon',
      author_email='',
      license='MIT',
      packages=['arcexport'],
      package_data={'arcexport': ['templates/*']},
      entry_points={
          'nbconvert.exporters': [
              'arcexport = arcexport:ArcExporter'
          ],
      })