import datetime
import time
from snappy import ProductIO
from snappy import HashMap
import os, gc
from snappy import GPF
import snappy
from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import QFileDialog
import geodaisy.converters as convert
from Section3.Dialog import Sentinelsat -Download data

def do_apply_orbit_file(source):
    print('\tApply orbit file...')
    parameters = HashMap()
    parameters.put('Apply-Orbit-File', True)
    output = GPF.createProduct('Apply-Orbit-File', parameters, source)
    return output


def do_thermal_noise_removal(source):
    print('\tThermal noise removal...')
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    output = GPF.createProduct('ThermalNoiseRemoval', parameters, source)
    return output


def do_calibration(source, polarization, pols):
    print('\tCalibration...')
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    if polarization == 'DH':
        parameters.put('sourceBands', 'Intensity_HH,Intensity_HV')
    elif polarization == 'DV':
        parameters.put('sourceBands', 'Intensity_VH,Intensity_VV')
    elif polarization == 'SH' or polarization == 'HH':
        parameters.put('sourceBands', 'Intensity_HH')
    elif polarization == 'SV':
        parameters.put('sourceBands', 'Intensity_VV')
    else:
        print("different polarization!")
    parameters.put('selectedPolarisations', pols)
    parameters.put('outputImageScaleInDb', False)
    output = GPF.createProduct("Calibration", parameters, source)
    return output


def do_speckle_filtering(source):
    print('\tSpeckle filtering...')
    parameters = HashMap()
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', 5)
    parameters.put('filterSizeY', 5)
    output = GPF.createProduct('Speckle-Filter', parameters, source)
    return output


def do_terrain_correction(source, proj, polarization):
    print('\tTerrain correction...')
    parameters = HashMap()
    parameters.put('demResamplingMethod', 'NEAREST_NEIGHBOUR')
    parameters.put('imgResamplingMethod', 'NEAREST_NEIGHBOUR')
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('pixelSpacingInMeter', 10.0)

    output = GPF.createProduct('Terrain-Correction', parameters, source)
    return output


def bandMathsProduct(source):
    print("\tDoing bandmaths...")
    global product
    params = HashMap()
    BandDescriptor = snappy.jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    targetBand = BandDescriptor()
    targetBand.name = 'Sigma0_VV'
    targetBand.type = 'float32'
    targetBand.expression = '(Sigma0_VV < 2.22E-2) ? 255 : 0'
    targetBands = snappy.jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand
    params.put('targetBands', targetBands)
    output = GPF.createProduct('BandMaths', params, source)
    print("\tBandmaths done...")

    return output



def main():
    print(path)
   

    if not os.path.exists(outpath):
        os.makedirs(outpath)
    ## well-known-text (WKT) file for subsetting (can be obtained from SNAP by drawing a polygon)
    
    ## UTM projection parameters
    proj = '''PROJCS["UTM Zone 4 / World Geodetic System 1984",GEOGCS["World Geodetic System 1984",DATUM["World Geodetic System 1984",SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],UNIT["degree", 0.017453292519943295],AXIS["Geodetic longitude", EAST],AXIS["Geodetic latitude", NORTH]],PROJECTION["Transverse_Mercator"],PARAMETER["central_meridian", -159.0],PARAMETER["latitude_of_origin", 0.0],PARAMETER["scale_factor", 0.9996],PARAMETER["false_easting", 500000.0],PARAMETER["false_northing", 0.0],UNIT["m", 1.0],AXIS["Easting", EAST],AXIS["Northing", NORTH]]'''

    for folder in os.listdir(path):
        gc.enable()
        gc.collect()
        sentinel_1 = ProductIO.readProduct(path +"\\manifest.safe")
        print(sentinel_1)

        loopstarttime=str(datetime.datetime.now())
        print('Start time:', loopstarttime)
        start_time       = time.time()

        ## Extract mode, product type, and polarizations from filename
        modestamp = path.split("_")[1]
        productstamp = path.split("_")[2]
        polstamp = path.split("_")[3]
        print(modestamp)

        polarization = polstamp[2:4]
        if polarization == 'DV':
            pols = 'VH,VV'
        elif polarization == 'DH':
            pols = 'HH,HV'
        elif polarization == 'SH' or polarization == 'HH':
            pols = 'HH'
        elif polarization == 'SV':
            pols = 'VV'
            
        else:
            print("Polarization error!")

       
        applyorbit = do_apply_orbit_file(sentinel_1)
        thermaremoved = do_thermal_noise_removal(applyorbit)
        calibrated = do_calibration(thermaremoved, polarization, pols)
        do_specle = do_speckle_filtering(calibrated)


        
        if (modestamp == 'IW' and productstamp == 'GRDH') or (modestamp == 'EW' and productstamp == 'GRDH'):
            down_tercorrected = do_terrain_correction(do_specle, proj, polarization)
            bandmath = bandMathsProduct(down_tercorrected)

            print("\tWriting Image....\n This may take few minutes depnding on you image size...")


            ProductIO.writeProduct(bandmath, outpath, 'GeoTIFF')
            
        elif modestamp == 'EW' and productstamp == 'GRDM':
            tercorrected = do_terrain_correction(subset, proj, polarization)
            bandMath = bandMathsProduct(tercorrected)

            ProductIO.writeProduct(bandMath, outpath, 'GeoTIFF')
        else:
            print("Different spatial resolution is found.")

        print('Done.')
        sentinel_1.dispose()
        sentinel_1.closeIO()
        print("--- %s seconds ---" % (time.time() - start_time))


def openFileNameDialog():
    global path

    path = QFileDialog.getExistingDirectory(None, 'Choose input folder', "")
    #print(Data_path)
def outputDirectory():
    global outpath
    outpath = QFileDialog.getExistingDirectory(None, 'Output Directory', "")

def Download_Data():
    print('triggered')




if __name__== "__main__":
    app = QtWidgets.QApplication([])
    call = uic.loadUi('preprocess.ui')
    call.pushbutton.clicked.connect(main)
    call.filepathbox.clicked.connect(openFileNameDialog)
    call.outputbox.clicked.connect(outputDirectory)
    call.download.clicked.connect(Download_data)
    call.show()
    app.exec()

    #main()

        
            
