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

REM If you prefer to use the C compiler from Visual Studio 2022, run this
REM script from the "Developer Command Prompt for VS2022" and remove the
REM `--mingw64` flag from the `python -m nuitka` call.

setlocal EnableExtensions
cd /d "%~dp0"

set "ORIGINAL_DIR=%CD%"
set "SHORT_DRIVE="
set "NUITKA_CACHE_DIR=%SystemDrive%\ncache"

if not exist "%NUITKA_CACHE_DIR%" mkdir "%NUITKA_CACHE_DIR%"
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%

call :try_map_drive P
if not defined SHORT_DRIVE call :try_map_drive Q
if not defined SHORT_DRIVE call :try_map_drive R
if not defined SHORT_DRIVE call :try_map_drive S
if not defined SHORT_DRIVE call :try_map_drive T
if not defined SHORT_DRIVE call :try_map_drive U
if not defined SHORT_DRIVE call :try_map_drive V
if not defined SHORT_DRIVE call :try_map_drive W
if not defined SHORT_DRIVE call :try_map_drive X
if not defined SHORT_DRIVE call :try_map_drive Y
if not defined SHORT_DRIVE call :try_map_drive Z

IF not defined SHORT_DRIVE (
    echo Could not create a short drive mapping for %ORIGINAL_DIR%.
    exit /b 1
)

call :run_build
set "BUILD_EXIT_CODE=%ERRORLEVEL%"

cd /d "%ORIGINAL_DIR%"
if defined SHORT_DRIVE subst %SHORT_DRIVE% /d >NUL 2>&1

exit /b %BUILD_EXIT_CODE%

:try_map_drive
subst %~1: "%ORIGINAL_DIR%" >NUL 2>&1
IF not ERRORLEVEL 1 set "SHORT_DRIVE=%~1:"
exit /b 0

:run_build
cd /d %SHORT_DRIVE%

SET PYTHON_VERSION=%PYMINFLUX_PYTHON_VERSION%
IF "%PYTHON_VERSION%"=="" SET PYTHON_VERSION=3.12

where uv >NUL 2>&1
IF ERRORLEVEL 1 (
    ECHO uv is required to build pyMINFLUX.
    exit /b 1
)

uv python install %PYTHON_VERSION%
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%

uv sync --locked --extra dev --python %PYTHON_VERSION% --managed-python --no-install-package zstandard
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%

uv run python -c "import pathlib, tomllib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])" > "%TEMP%\pyminflux_version.txt"
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%
set /p VERSION=<"%TEMP%\pyminflux_version.txt"
del "%TEMP%\pyminflux_version.txt"

if "%VERSION%"=="" (
    echo Could not determine the project version
    exit /b 1
)

uv run python -c "import os, vispy; print(os.path.join(os.path.dirname(vispy.__file__), 'glsl'))" > "%TEMP%\pyminflux_vispy.txt"
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%
set /p VISPY_GLSL_DIR=<"%TEMP%\pyminflux_vispy.txt"
del "%TEMP%\pyminflux_vispy.txt"

if "%VISPY_GLSL_DIR%"=="" (
    echo Could not determine vispy glsl directory
    exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build from a substituted drive and a short cache root to avoid Windows
REM path-length issues during the SCons link step.
REM Note: if `--mingw64 --clang` causes Windows Defender to give false positives,
REM use `--msvc=latest` instead.
uv run python -m nuitka pyminflux/main.py -o pyMINFLUX ^
--mingw64 --clang ^
--assume-yes-for-downloads ^
--windows-console-mode=disable ^
--noinclude-default-mode=error ^
--standalone ^
--include-module=scipy.special._special_ufuncs ^
--include-module=vispy.app.backends._pyside6 ^
--include-module=pydoc ^
--include-data-dir="%VISPY_GLSL_DIR%=vispy/glsl" ^
--windows-icon-from-ico=pyminflux\\ui\\assets\\Logo_v3.ico ^
--enable-plugin=pylint-warnings ^
--enable-plugin=pyside6 ^
--noinclude-default-mode=nofollow ^
--file-version=%VERSION% ^
--product-version=%VERSION% ^
--remove-output ^
--output-dir=.\dist
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%

move dist\main.dist dist\pyMINFLUX
IF ERRORLEVEL 1 exit /b %ERRORLEVEL%

exit /b 0
