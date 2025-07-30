from setuptools import setup, find_packages


setup(
    name='volworld_aws_api_common',
    version='0.1.187',
    license='MIT',
    author="Che-Wri, Chang",
    author_email='gobidesert.mf@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='volworld',
    install_requires=[
          'aenum',
          'volworld_common',
      ],

)
