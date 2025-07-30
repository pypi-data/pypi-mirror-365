@echo off
REM Script de publication sur PyPI
REM Usage: publish.bat

echo 🚀 Publication du plugin mkdocs-cc-license-plugin...

REM Vérification des prérequis
echo Vérification des prérequis...
python -c "import twine, build" 2>nul
if errorlevel 1 (
    echo Installation des outils de publication...
    pip install build twine
)

REM Nettoyage des builds précédents
echo Nettoyage des builds précédents...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

REM Construction du package
echo Construction du package...
python -m build

REM Vérification du package
echo Vérification du package...
python -m twine check dist/*

echo ✅ Package construit et vérifié avec succès !
echo.
echo Fichiers générés dans dist/ :
dir dist

echo.
echo Pour publier sur PyPI :
echo   1. Test PyPI : twine upload --repository testpypi dist/*
echo   2. PyPI prod : twine upload dist/*
echo.
set /p upload="Voulez-vous publier sur Test PyPI maintenant ? (y/N): "
if /i "%upload%"=="y" (
    echo Publication sur Test PyPI...
    python -m twine upload --repository testpypi dist/*
    echo.
    echo ✅ Publié sur Test PyPI !
    echo Testez avec : pip install --index-url https://test.pypi.org/simple/ mkdocs-cc-license-plugin
)

echo.
echo Publication terminée ! 🎉
