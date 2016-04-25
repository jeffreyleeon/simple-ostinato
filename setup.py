from setuptools import setup


setup(
    name='simple_ostinato',
    version='0.0.1',
    include_package_data=True,
    description='simple ostinato python client',
    url='http://github.com/little-dude/ostinato-client',
    author='Corentin Henry',
    author_email='corentin.henry@gmail.com',
    license='GPLv3',
    packages=['simple_ostinato'],
    package_data={},
    install_requires=[line for line in open('requirements.txt')],
)