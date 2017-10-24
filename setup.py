from setuptools import setup
setup(
   name='sendclient',
   version=0.1,
   description='Unofficial Firefox Send client',
   long_description='Command-line client to upload and download encrypted files from a Send server such as https://send.firefox.com',
   url='https://github.com/ehuggett/send-cli',
   author='Edmund Huggett',
   author_email='edmund.huggett@fsfe.org',
   license='GNU General Public License v3 or later (GPLv3+)',
   packages=['sendclient'],
   scripts =  ['scripts/send-cli'],
   install_requires=[
      'pycryptodomex',
      'requests',
      'requests-toolbelt',
      'tqdm',
      'urllib3'
   ],
   setup_requires=['pytest-runner'],
   tests_require=['pytest'],
   classifiers=[
        'Topic :: Communications :: File Sharing',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
   ],
)
