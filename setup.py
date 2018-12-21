try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'SmurfFinder for 100 Thieves Application',
    'author': 'Harry Veilleux',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'harryveilleux@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['thieves'],
    'scripts': [],
    'name': '100T SmurfFinder'
}

setup(**config)
