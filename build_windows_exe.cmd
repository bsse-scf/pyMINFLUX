@ECHO OFF
REM Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
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
setlocal

SET VERSION=0.2.0

IF "%ANACONDA_HOME%"=="" ECHO Please set environment variable ANACONDA_HOME. && exit /b

REM Create and activate a dedicated env
call conda create -n pyminflux-build python=3.10 -y
call conda activate pyminflux-build

REM Install dependencies
poetry.exe install

REM Delete build and dist folders
rmdir /s /q build
rmdir /s /q dist

REM TBuild the executable
pyinstaller.exe pyminflux\main.py ^
--clean ^
--windowed ^
--hidden-import="sklearn.neighbors._typedefs" ^
--hidden-import="sklearn.metrics._pairwise_distances_reduction._datasets_pair" ^
--hidden-import="sklearn.metrics._pairwise_distances_reduction._middle_term_computer" ^
--noconsole ^
--icon pyminflux\\ui\\assets\\Logo_v3.ico ^
--name pyMINFLUX ^
--noconfirm

REM Copy the icon
copy pyminflux\\ui\\assets\\Logo_v3.png dist\\pyMINFLUX

REM Zip the folder
set TMP_FOLDER=%~dp0dist\tmp
IF NOT EXIST "%TMP_FOLDER%" MKDIR "%TMP_FOLDER%"
set INPUT_FOLDER=%~dp0dist\pyMINFLUX
XCOPY /E /I "%INPUT_FOLDER%" "%TMP_FOLDER%\pyMINFLUX"
set OUTPUT_FILE=%~dp0dist\pyMINFLUX_%VERSION%_win.zip
powershell.exe -nologo -noprofile -command "& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::CreateFromDirectory('%TMP_FOLDER%', '%OUTPUT_FILE%'); }"

REM Remove the conda environment
call conda deactivate
call conda env remove -n pyminflux-build
IF EXIST "%ANACONDA_HOME%"\envs\pyminflux-build rmdir /s /q "%ANACONDA_HOME%"\envs\pyminflux-build
