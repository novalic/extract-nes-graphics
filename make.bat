@echo off
setlocal

if "%~1"=="" goto usage
if "%~1"=="install" goto install
if "%~1"=="run" goto run
if "%~1"=="test" goto test
if "%~1"=="coverage" goto coverage
if "%~1"=="check" goto check
if "%~1"=="fix" goto fix
if "%~1"=="clean" goto clean
goto usage

:install
uv sync
goto :eof

:run
uv run python extract_graphics.py
goto :eof

:test
uv run pytest
goto :eof

:coverage
uv run coverage run -m pytest
uv run coverage report -m
goto :eof

:check
uv run ruff check .
goto :eof

:fix
uv run ruff check --fix .
goto :eof

:clean
if exist .venv rmdir /s /q .venv
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .coverage del /q .coverage
if exist htmlcov rmdir /s /q htmlcov
for /f "delims=" %%d in ('dir /s /b /ad __pycache__ 2^>nul') do rmdir /s /q "%%d"
goto :eof

:usage
echo Usage: make.bat [install^|run^|test^|coverage^|check^|fix^|clean]
exit /b 1
