@ECHO OFF
REM Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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
REM limitations under the License.

REM To use the C compiler from Visual Studio 2022, run this script from the
REM "Developer Command Prompt for VS2022" and remove the `--mingw64` from the
REM `python -m nuitka` call.
setlocal

SET VERSION=0.6.0
SET PYTHON_VERSION=3.12

IF "%ANACONDA_HOME%"=="" ECHO Please set environment variable ANACONDA_HOME. && exit /b

REM Create and activate a dedicated env
call conda create -n pyminflux-build python=%PYTHON_VERSION% -y
call conda activate pyminflux-build

REM Install dependencies
poetry.exe install

REM Remove zstandard (to reduce the risk of false positives in Windows Defender
pip unintstall zstandard -y

REM Determine the path to the vispy glsl directory
for /f "delims=" %%i in ('python -c "import vispy, os; print(os.path.join(os.path.dirname(vispy.__file__), 'glsl'))"') do set VISPY_GLSL_DIR=%%i

REM Check if the path was found
if "%VISPY_GLSL_DIR%"=="" (
    echo Could not determine vispy glsl directory
    exit /b 1
)

REM Delete build and dist folders
rmdir /s /q build
rmdir /s /q dist

REM Build the executable
REM Note: if `--mingw64 --clang` causes Windows Defender to give false positives,
REM use `--msvc=latest` instead
python -m nuitka pyminflux/main.py -o pyMINFLUX ^
--mingw64 --clang ^
--assume-yes-for-downloads ^
--windows-console-mode=disable ^
--noinclude-default-mode=error ^
--standalone ^
--include-module=scipy.special._special_ufuncs ^
--include-module=vispy.app.backends._pyside6 ^
--include-module=pydoc ^
--include-data-dir=%VISPY_GLSL_DIR%=vispy/glsl ^
--windows-icon-from-ico=pyminflux\\ui\\assets\\Logo_v3.ico ^
--enable-plugin=pylint-warnings ^
--enable-plugin=pyside6 ^
--noinclude-default-mode=nofollow ^
--remove-output ^
--output-dir=./dist

REM Rename che created folder
move dist\main.dist dist\pyMINFLUX

REM Remove the conda environment
call conda deactivate
call conda env remove -n pyminflux-build -y
IF EXIST "%ANACONDA_HOME%"\envs\pyminflux-build rmdir /s /q "%ANACONDA_HOME%"\envs\pyminflux-build
