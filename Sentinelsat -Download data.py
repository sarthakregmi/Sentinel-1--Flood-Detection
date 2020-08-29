
#This code reads the shapefiles and GeoJSON file and downloads the sentinel image of that area
#Coded_by_Sarthak-Science_hub_Nepal

import time
import datetime
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import geopandas as gpd
import ogr, os
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import QFileDialog
def login():
    
    user_name = call.usernamebox.text()
    password = call.Passwordbox.text()
    global api
    api = SentinelAPI(user_name , password, 'https://scihub.copernicus.eu/dhus')
    dataimport()

def dataimport():
    #print(Data_path[0])


    #Data_path = call.filepathbox.text()
    global start_date, end_date

    start_date = call.startdatebox.text()
    end_date = call.enddatebox.text()
    global footprint
    if Data_path[0].lower().endswith(('.geojson')):
        print("its geojson")
        footprint = geojson_to_wkt(read_geojson(Data_path[0]))
        #print(footprint)
    elif Data_path[0].lower().endswith(('.shp')):
        #print("its shape file")
        myshpfile = gpd.read_file(Data_path[0])
       
        footprint = myshpfile.to_file("file.geojson", driver='GeoJSON')
    elif Data_path[0].lower().endswith(('.wkt')):
        footprint = read_wkt(Data_path[0])
    datadownload()
def datadownload():

    if call.sentinel2box.isChecked() == True:

        products = api.query(footprint, date=(start_date, date(2020,4,29)),platformname='Sentinel-2', cloudcoverpercentage = (0, 30))
        #print("Downloading Sentinel 2 data.")

    if call.sentinel1box.isChecked() == True:
        #print("Downloading sentinel 1 data")
        products = api.query(footprint, date =(start_date , end_date), platformname ='Sentinel-1', producttype = 'GRD')

    api.download_all(products)


def openFileNameDialog():
    global Data_path

    Data_path = QFileDialog.getOpenFileName(None,'Open File',"","geojson files (*.geojson);;Shape Files (*.shp);; wkt file(*.wkt)")
    

if __name__ =='__main__':

     app = QtWidgets.QApplication([])
     call = uic.loadUi('GUI1.ui')
     call.pushButton.clicked.connect(login)
     call.toolButton.clicked.connect(openFileNameDialog)
     call.show()
     app.exec()
