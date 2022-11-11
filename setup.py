from setuptools import setup, find_packages
from distutils.util import convert_path
from setuptools.extension import Extension
from numpy import get_include
from Cython.Build import cythonize
import sysconfig
import os


extra_compile_args = sysconfig.get_config_var('CFLAGS')
if extra_compile_args is not None:
    extra_compile_args = extra_compile_args.split()
else:
    extra_compile_args = []

if os.name == 'nt':
    extra_compile_args += ["/O3"]
else:
    extra_compile_args += ["-O3"]


main_ns = {}
ver_path = convert_path('pyminflux/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name='pyminflux',
    version=main_ns['__version__'],
    url='https://git.bsse.ethz.ch/pontia/pyminflux',
    author='Aaron Ponti',
    author_email='aaron.ponti@bsse.ethz.ch',
    description='Reader, processor, and viewer of MINFLUX raw data.',
    license='TBD',
    packages=find_packages(),
    ext_modules=cythonize([
        Extension(
            "pyminflux.processor.processor",
            ["pyminflux/processor/processor.pyx"], include_dirs=[get_include()],
            extra_compile_args=extra_compile_args
            ),
        ], language_level="3"
    ),
    install_requires=[
        'Cython',
        'jupyter',
        'matplotlib',
        'numpy',
        'pandas',
        'pyqt5',
        'pyqtgraph',
        'scipy',
        'scikit-learn'
    ],
    python_requires='>=3.9',
)

