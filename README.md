# Geographically Weighted Regression(GWR) Plugin for QGIS
A QGIS plugin for Geographically Weighted Regression(GWR).

___
### Installation - Windows

**1)** Open QGIS:

Go to `Plugins` -> `Manage and Install plugins` -> `Settings` -> `Show also experimental plugins` 

In `All plugins` tab, look for `Geographically Weighted Regression` and tick the checkbox.  
A new icon for Geographically Weighted Regression will appear on the QGIS main panel and in the Vector Menu.

**2)** Open QGIS:

Download the zip folder of the repository at:
https://github.com/XiangyangSong/gwr_processing/archive/refs/heads/qgis3gwr1.zip

Open QGIS 3 and go to `Plugins` -> `Install from ZIP`

Select the downloaded zip folder and press `Install plugin`. The icon for the GWR plugin will appear in the list of the installed plugins. Tick the Checkbox to activate it. The plugin will appear in the Vector menu.

**Note**: In case of errors rising from the Scipy,Spglm,Shapely package, open `OSGeo4W Shell` installed with QGIS3 as `Administrator` and type:
```sh
 $ python -m pip install scipy -U
 $ python -m pip install spglm -U
 $ python -m pip install shapely -U
```

In case of does not find python, open `OSGeo4W Shell` installed with QGIS3 as `Administrator` and type(e.g. jump to the python environment directory in QGIS folder where installed in your computer):
```sh 
 $ cd C:\Program Files\QGIS 3.16\apps\Python37
```
If there is a error of pip, open `OSGeo4W Shell` installed with QGIS3 as `Administrator` and type:
- ModuleNotFoundError: No module named 'pip'
```sh 
$ python -m ensurepip
$ python -m pip install --upgrade pip
```


___
### Changeset

##### Changeset 01/2022
- Fixed an issue of export feature type error. 

##### Changeset 02/2022
- Fixed an issue that the name of spatial kernel in the Geographically Weighted Regression (GWR) remained unchanged in the output summary .txt file. 
- Changed the way of importing geographical coordinates from selecting coordinates attributes inside shapefile layer to opening .csv sheet file. As a result, user is required to proceed one additional step after opening the .csv file: mannually type the names of two fields indicating coordinates x and y in the .csv file opened. 
- Fixed the unit problem of fixed and adaptive kernel type. The unit for fixed kernel type is "meters" instead of kilometers in our plugin. 
- Updated ShortHelpString.html document to provide more information on help page in the plugin, with an improved layout.
