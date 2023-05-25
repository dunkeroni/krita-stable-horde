REM Prompt user for version number
set /p version="Enter the version number of the plugin you want to archive: "

REM Create plugin name with version
set "plugin_name=AIHorde-Krita-Importable-%version%"

REM Zip krita_AIhorde.desktop and krita_AIhorde folder, put results in Releases folder
"C:\Program Files\7-Zip\7z.exe" a -r "Releases\%plugin_name%.zip" krita_AIhorde.desktop krita_AIhorde