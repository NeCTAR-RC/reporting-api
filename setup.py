from setuptools import setup, find_packages
from pip.req import parse_requirements

version = '0.1.0'

requirements = parse_requirements('requirements.txt', session=False)

setup(name='reporting-api',
      version=version,
      description='OpenStack Reporting API',
      author='NeCTAR',
      author_email='',
      url='https://github.com/NeCTAR-RC/reporting-api',
      license='Apache 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      install_requires=[str(r.req) for r in requirements],
      scripts=['bin/reporting-api'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Paste',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Database :: Front-Ends',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
      ]
)
