@ECHO OFF
REM Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
REM
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.
REM You may obtain a copy of the License at
REM
REM      http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing, software
REM distributed under the License is distributed on an "AS IS" BASIS,
REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM See the License for the specific language governing permissions and
REM  limitations under the License.
REM

REM To use the C compiler from Visual Studio 2022, run this script from the
REM "Developer Command Prompt for VS2022" and remove the `--mingw64` from the
REM `python -m nuitka` call.
setlocal

SET VERSION=0.4.1
SET PYTHON_VERSION=3.11

IF "%ANACONDA_HOME%"=="" ECHO Please set environment variable ANACONDA_HOME. && exit /b

REM Create and activate a dedicated env
call conda create -n pyminflux-build python=%PYTHON_VERSION% -y
call conda activate pyminflux-build

REM Install 7zip for compression
call conda install 7zip -y

REM Install nuitka
python -m pip install nuitka ordered_set zstandard

REM Install dependencies
poetry.exe install

REM Delete build and dist folders
rmdir /s /q build
rmdir /s /q dist

REM Build the executable
python -m nuitka pyminflux/main.py -o pyMINFLUX ^
--mingw64 ^
--assume-yes-for-downloads ^
--disable-console ^
--noinclude-default-mode=error ^
--standalone ^
--onefile ^
--windows-icon-from-ico=pyminflux\\ui\\assets\\Logo_v3.ico ^
--enable-plugin=pylint-warnings ^
--enable-plugin=pyside6 ^
--noinclude-pytest-mode=nofollow ^
--noinclude-setuptools-mode=nofollow ^
--remove-output ^
--output-dir=./dist

REM Zip the executable
cd dist
set INPUT_FILE=pyMINFLUX.exe
set OUTPUT_FILE=pyMINFLUX_%VERSION%_win.zip
7z.exe a -tzip "%OUTPUT_FILE%" "%INPUT_FILE%" > NUL:

REM Remove the conda environment
call conda deactivate
call conda env remove -n pyminflux-build -y
IF EXIST "%ANACONDA_HOME%"\envs\pyminflux-build rmdir /s /q "%ANACONDA_HOME%"\envs\pyminflux-build
