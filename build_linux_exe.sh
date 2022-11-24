# Required dependencies in Ubuntu
#
# $ conda install libpython-static
# $ conda install ccache
# $ sudo apt install patchelf
python -m nuitka --jobs=8 --include-module=OpenGL --noinclude-default-mode=error --follow-imports --disable-console --assume-yes-for-downloads --enable-plugin=pylint-warnings --standalone pyminflux/main.py --enable-plugin=numpy --enable-plugin=pyside6 --output-dir=./dist
mv dist/main.dist/main dist/main.dist/pyminflux
mv dist/main.dist/main dist/pyminflux
