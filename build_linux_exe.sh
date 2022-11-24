# Required dependencies in Ubuntu
#
# $ conda install libpython-static
# $ conda install ccache
# $ sudo apt install patchelf
python -m nuitka pyminflux/main.py --jobs=8 --assume-yes-for-downloads --disable-console --noinclude-default-mode=error --follow-imports --standalone --include-module=OpenGL --enable-plugin=pylint-warnings --enable-plugin=numpy --enable-plugin=pyside6 --output-dir=./dist
mv dist/main.dist/main dist/main.dist/pyminflux
mv dist/main.dist dist/pyminflux
