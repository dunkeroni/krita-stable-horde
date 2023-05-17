RMDIR /S /Q "%AppData%\krita\pykrita\krita_AIhorde"
DEL /S /Q "%AppData%\krita\pykrita\krita_AIhorde.desktop"

xcopy "%cd%\krita_AIhorde" "%AppData%\krita\pykrita\krita_AIhorde\" /e
xcopy "%cd%\krita_AIhorde.desktop" "%AppData%\krita\pykrita\" /i /y