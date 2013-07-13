from distutils.core import setup

setup(name='nikeplusapi',
      version='0.1',
      description='Export nikeplus data to CSV format',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='https://github.com/durden/nikeplus',
      packages=['nikeplus'],
      entry_points={
        "console_scripts": [
            "nikeplus = nikeplus.export:main",
        ]
    },
)
