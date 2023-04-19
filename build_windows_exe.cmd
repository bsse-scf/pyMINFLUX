REM To build, use the following command
pyinstaller.exe pyminflux\main.py ^
--windowed ^
--hidden-import="sklearn.metrics._pairwise_distances_reduction._datasets_pair" ^
--hidden-import="sklearn.metrics._pairwise_distances_reduction._middle_term_computer" ^
--noconsole ^
--icon pyminflux\\ui\\assets\\Logo_v3.ico ^
--name pyMINFLUX ^
--noconfirm

REM Copy the icon
copy pyminflux\\ui\\assets\\Logo_v3.png dist\\pyMINFLUX