#prompt user for version number
echo "Enter the version number of the plugin you want to archive"
read version

#create plugin name with version
plugin_name="AIHorde-Krita-Importable-$version"

#zip krita_AIhorde.desktop and krita_AIhorde folder, put results in Releases folder
zip -r Releases/$plugin_name.zip krita_AIhorde.desktop krita_AIhorde
