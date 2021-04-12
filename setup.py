from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('pyminflux/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name='pyMINFLUX',
    version=main_ns['__version__'],
    url='https://git.bsse.ethz.ch/pontia/pyminflux',
    author='Aaron Ponti',
    author_email='aaron.ponti@bsse.ethz.ch',
    description='Reader, processor, and viewer of MINFLUX raw data.',
    license='TBD',
    packages=find_packages(),
    install_requires=[
        'numpy >= 1.20.0',
        'pandas >= 1.2.0',
        'pptk >= 0.1.0',
        'open3d >= 0.12.0',
    ],
    python_requires='>=3.6, <3.8',
)
