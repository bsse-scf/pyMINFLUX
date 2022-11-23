python -m nuitka pyminflux/main.py --jobs=8 --assume-yes-for-downloads --disable-console --noinclude-default-mode=error --follow-imports --standalone --macos-create-app-bundle --macos-app-icon=resources/icon.png --include-module=OpenGL --enable-plugin=pylint-warnings --enable-plugin=numpy --enable-plugin=pyside6 --output-dir=./dist

mv dist/main.dist/main dist/main.dist/pyminflux
mv dist/main.dist/main dist/pyminflux
