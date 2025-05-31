@echo off
set PYTHON=C:/Users/gmful/AppData/Local/Programs/Python/Python312/python.exe

echo Formatting with Black...
%PYTHON% -m black .

echo Sorting imports with isort...
%PYTHON% -m isort .

echo Running flake8 linting...
%PYTHON% -m flake8 .

echo Checking for unused code with vulture...
%PYTHON% -m vulture .
