from setuptools import setup
import io

import nikeplusapi

# Take from Jeff Knupp's excellent article:
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []

    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())

    return sep.join(buf)

long_description = read('README.md')

setup(name='nikeplusapi',
      version=nikeplusapi.__version__,
      description='Export nikeplus data to CSV format',
      long_description=long_description,
      license='MIT',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='https://github.com/durden/nikeplus',
      packages=['nikeplusapi'],
      platforms='any',
      classifiers= [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: System :: Archiving'],
      entry_points={
        "console_scripts": [
            "nikeplusapi = nikeplusapi.export:main",
        ]
      },
)
