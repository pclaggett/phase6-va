# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# County python scripts
# Colin Stief
# ---------------------------------------------------------------------------

## Import modules
import arcpy, os, time, sys
from arcpy.sa import *

## Checkout extentions
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.AddMessage("Checking out Spatial")
    arcpy.CheckOutExtension("Spatial")
else:
    arcpy.AddError("Unable to get spatial analyst extension")
    arcpy.AddMessage(arcpy.GetMessages(0))
    sys.exit(0)


## Define functions
def cleanGDB(GDB):
    arcpy.env.workspace = GDB
    list_rasters = arcpy.ListRasters()
    for raster in list_rasters:
        arcpy.AddMessage("Deleting: " + raster)
        arcpy.Delete_management(raster)
    arcpy.AddMessage("Deleted all rasters in: " + GDB)


def createTemplate(dir_landuse):
    dir_counties = os.path.join(dir_landuse, "Counties")
    os.chdir(dir_counties)
    list_counties = os.walk(".").next()[1]
    for county in list_counties:

        dir_temp = os.path.join(dir_counties, county, "Temp")
        dir_temp_1m = "Temp_1m.gdb"
        dir_temp_10m = "Temp_10m.gdb"
        dir_outputs = os.path.join(dir_counties, county, "Output")
        dir_outputs_1m = "Final_1m.gdb"
        dir_outputs_10m = "Final_10m.gdb"
        dir_outputs_tiffs = os.path.join(dir_counties, county, "Output", "Final_Tiffs")

        if not os.path.exists(dir_temp):
            os.mkdir(dir_temp)
        if not os.path.exists(dir_outputs):
            os.mkdir(dir_outputs)
        if not os.path.exists(dir_outputs_tiffs):
            os.mkdir(dir_outputs_tiffs)

        arcpy.CreateFileGDB_management(dir_temp, dir_temp_1m)
        arcpy.CreateFileGDB_management(dir_temp, dir_temp_10m)
        arcpy.CreateFileGDB_management(dir_outputs, dir_outputs_1m)
        arcpy.CreateFileGDB_management(dir_outputs, dir_outputs_10m)


def copyFinalRasters(county, CountyDataGDB, Output1mGDB):
    arcpy.env.workspace = CountyDataGDB
    list_rasters = arcpy.ListRasters()
    for raster in list_rasters:
        if raster[11:] == "WLO_1m":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, raster))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, raster))
        elif raster[11:] == "WLT_1m":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, raster))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, raster))
        elif raster[11:] == "WLF_1m":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, raster))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, raster))
        elif raster[11:] == "WAT":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, raster + "_1m"))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, raster + "_1m"))
        elif raster[11:] == "IR":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, raster + "_1m"))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, raster + "_1m"))
        elif raster[11:] == "INR":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, raster + "_1m"))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, raster + "_1m"))
        elif raster[11:] == "TCIcc":
            arcpy.AddMessage("Copying " + os.path.join(Output1mGDB, county + "_TCoI_1m"))
            arcpy.CopyRaster_management(raster, os.path.join(Output1mGDB, county + "_TCoI_1m"))


def developmentModel(county, CountyDataGDB, Output1mGDB, Temp1mGBD):
    time_start = time.clock()

    INR = os.path.join(Output1mGDB, county + "_INR_1m")  # exists

    if arcpy.Exists(INR):

        FS113 = FocalStatistics(INR, "Circle 113 CELL", "SUM", "DATA")
        NULL113 = SetNull(FS113, 1, "Value <= 3000")  # Set all values <= 3000 to null, and other values to 1
        NULL113.save(county + "_DEV113")

        cleanGDB(Temp1mGBD)  ## !!WARNING!! This deletes all rasters in the provided geodatabase
        arcpy.env.workspace = CountyDataGDB

        FS18 = FocalStatistics(INR, "Circle 18 CELL", "SUM", "DATA")
        NULL18 = SetNull(FS18, 1, "Value <= 140")
        NULL18.save(county + "_DEV18")

        cleanGDB(Temp1mGBD)  ## !!WARNING!! This deletes all rasters in the provided geodatabase
        arcpy.env.workspace = CountyDataGDB

        FS27 = FocalStatistics(INR, "Circle 27 CELL", "SUM", "DATA")
        NULL27 = SetNull(FS27, 1, "Value <= 140")
        NULL27.save(county + "_DEV27")

        cleanGDB(Temp1mGBD)  ## !!WARNING!! This deletes all rasters in the provided geodatabase
        arcpy.env.workspace = CountyDataGDB

        FS37 = FocalStatistics(INR, "Circle 37 CELL", "SUM", "DATA")
        NULL37 = SetNull(FS37, 1, "Value <= 140")
        NULL37.save(county + "_DEV37")

        cleanGDB(Temp1mGBD)  ## !!WARNING!! This deletes all rasters in the provided geodatabase
        arcpy.env.workspace = CountyDataGDB

    else:
        arcpy.AddMessage("Can't find INR raster at: " + INR)

    arcpy.AddMessage("That took " + str((time.clock() - time_start) / 60) + " minutes")


def extractCropPasture(county, CountyDataGDB, Output1mGDB):
    if county == "ARLI_51013":

        time_start = time.clock()
        arcpy.AddMessage("Starting to extract crops and pastures...")

        LC = os.path.join(CountyDataGDB, county + "_LaCoTC")  # Base landcover dataset, exists
        PAS = os.path.join(Output1mGDB, county + "_PAS_1m")  # Worldview class 81, does not exist yet
        CRP = os.path.join(Output1mGDB, county + "_CRP_1m")  # Worldview class 82, does not exist yet

        raster_pasture = SetNull(LC, "1", "VALUE <> 81")
        if raster_pasture.maximum > 0:
            arcpy.AddMessage("Saving the pasture to: " + PAS)
            raster_pasture.save(PAS)
        else:
            arcpy.AddMessage("No pasture in this county")

        raster_crop = SetNull(LC, "1", "VALUE <> 82")
        if raster_crop.maximum > 0:
            arcpy.AddMessage("Saving the crops to: " + CRP)
            raster_crop.save(CRP)
        else:
            arcpy.AddMessage("No crops in this county")

        arcpy.AddMessage("That took " + str((time.clock() - time_start) / 60) + " minutes")


def copyFinalLandcover(county, CountyDataGDB):
    time_start = time.clock()
    dir_landcover = r"\\Ccsvr01\d\GIS\Conservation_Innovation\Classification_Resources\LandUseConversion\__P6ModelInputs\_CC_LC_Clipped.gdb"
    arcpy.env.workspace = dir_landcover
    list_rasters = arcpy.ListRasters()
    for raster in list_rasters:
        if county == raster[:-7]:
            arcpy.AddMessage("Copying from " + os.path.join(dir_landcover, raster))
            arcpy.AddMessage("Copying to " + os.path.join(CountyDataGDB, raster))
            arcpy.CopyRaster_management(os.path.join(dir_landcover, raster), os.path.join(CountyDataGDB, raster))
            arcpy.AddMessage("That took " + str((time.clock() - time_start) / 60) + " minutes")


## Start main block
dir_letter = arcpy.GetParameterAsText(0)

dir_landuse = r"C:\_VA_P6_Landuse_" + dir_letter
dir_counties = os.path.join(dir_landuse, "Counties")
os.chdir(dir_counties)
list_counties = os.walk(".").next()[1]
for county in list_counties:

    ## Current county and directory
    dir_county = os.path.join(dir_counties, county)

    ## County data and other resources
    ResourceGDB = os.path.join(dir_landuse, "Resources.gdb")
    CountyDataGDB = os.path.join(dir_counties, county, county + ".gdb")

    ## Temporary files
    Temp1mGBD = os.path.join(dir_counties, county, "Temp", "Temp_1m.gdb")
    Temp10mGDB = os.path.join(dir_counties, county, "Temp", "Temp_10m.gdb")
    TempDirectory = os.path.join(dir_counties, county, "Temp")

    ## Outputs
    Output1mGDB = os.path.join(dir_counties, county, "Output", "Final_1m.gdb")
    Output10mGDB = os.path.join(dir_counties, county, "Output", "Final_10m.gdb")
    TifDirectory = os.path.join(dir_counties, county, "Output", "Final_Tifs")

    ## Environments
    arcpy.env.workspace = CountyDataGDB
    arcpy.env.scratchWorkspace = Temp1mGBD
    arcpy.env.overwriteOutput = True
    arcpy.env.parallelProcessingFactor = "100%"
    arcpy.env.extent = os.path.join(CountyDataGDB, county + "_LaCoTC")  # Extent set to impervious roads
    arcpy.env.snapRaster = os.path.join(CountyDataGDB, county + "_LaCoTC")  # Snap raster set to impervious roads
    coord_data = os.path.join(ResourceGDB, "Phase6_Snap")
    arcpy.env.outputCoordinateSystem = arcpy.Describe(coord_data).spatialReference

    ## 1 meter LU Rasters - Listed in Hierarchial Order:
    IR = os.path.join(Output1mGDB, county + "_IR_1m")  # exists
    INR = os.path.join(Output1mGDB, county + "_INR_1m")  # exists
    TCI = os.path.join(Output1mGDB, county + "_TCoI_1m")  # exists
    WAT = os.path.join(Output1mGDB, county + "_WAT_1m")  # exists
    WLT = os.path.join(Output1mGDB, county + "_WLT_1m")  # exists if the county has any
    WLF = os.path.join(Output1mGDB, county + "_WLF_1m")  # exists if the county has any
    WLO = os.path.join(Output1mGDB, county + "_WLO_1m")  # exists if the county has any
    FOR = os.path.join(Output1mGDB, county + "_FOR_1m")  # does not exist yet
    TCT = os.path.join(Output1mGDB, county + "_TCT_1m")  # does not exist yet
    MO = os.path.join(Output1mGDB, county + "_MO_1m")  # does not exist yet
    FTG = os.path.join(Output1mGDB, county + "_FTG_1m")  # does not exist yet
    FINR = os.path.join(Output1mGDB, county + "_FINR_1m")  # does not exist yet
    TG = os.path.join(Output1mGDB, county + "_TG_1m")  # does not exist yet
    PAS = os.path.join(Output1mGDB, county + "_PAS_1m")  # exists if the county has any
    CRP = os.path.join(Output1mGDB, county + "_CRP_1m")  # exists if the county has any

    ## Other rasters:
    BAR = os.path.join(CountyDataGDB, county + "_Barren")
    BEACH = os.path.join(CountyDataGDB, county + "_MOBeach")
    DEV113 = os.path.join(CountyDataGDB, county + "_DEV113")
    DEV37 = os.path.join(CountyDataGDB, county + "_DEV37")
    DEV27 = os.path.join(CountyDataGDB, county + "_DEV27")
    DEV18 = os.path.join(CountyDataGDB, county + "_DEV18")
    FEDS = os.path.join(CountyDataGDB, county + "_FedPark")
    FINR_LU = os.path.join(CountyDataGDB, county + "_FracINR")
    FTG_LU = os.path.join(CountyDataGDB, county + "_FracTG")
    INST = os.path.join(CountyDataGDB, county + "_TurfNT")
    T_LANDUSE = os.path.join(CountyDataGDB, county + "_TgLU")
    M_LANDUSE = os.path.join(CountyDataGDB, county + "_MoLU")
    LV = os.path.join(CountyDataGDB, county + "_LV")
    MINE = os.path.join(CountyDataGDB, county + "_ExtLFill")
    PARCELS = os.path.join(CountyDataGDB, county + "_Parcels")
    ROW = os.path.join(CountyDataGDB, county + "_RoW")
    SS = os.path.join(CountyDataGDB, county + "_SS")
    TC = os.path.join(CountyDataGDB,
                      county + "_TC")  # trees over pervious surfaces = 41 + 42 + 61 + all classes over 100 (except 101, 121, 122) (This includes 43 as well)
    TREES = os.path.join(CountyDataGDB, county + "_MOTrees")
    HERB = os.path.join(CountyDataGDB, county + "_Herb")

    ## Tasks
    # createTemplate(dir_landuse)
    # copyFinalRasters(county, CountyDataGDB, Output1mGDB)
    # developmentModel(county, CountyDataGDB, Output1mGDB, Temp1mGBD)
    # extractCropPasture(county, CountyDataGDB, Output1mGDB)
    # copyFinalLandcover(county, CountyDataGDB)

    ## Models

    ## TURF MODEL
    # This model uses the following:
    # BAR, DEV113, FEDS, FINR_LU, FTG_LU, INST, LV, PARCELS, ROW

    # TURF 1: Mosaic All Non-road Impervious Surfaces
    # Skipping this because we already have INR

    # TURF 2: Create Herbaceous Layer
    if arcpy.Exists(county + "_Herb"):
        arcpy.AddMessage("Herbaceous Layer Exists")
        HERB = os.path.join(CountyDataGDB, county + "_Herb")
    else:
        time_start = time.clock()
        rasLocation = CountyDataGDB
        inRasters = Raster(BAR), Raster(LV)
        arcpy.MosaicToNewRaster_management(inRasters, rasLocation, county + "_Herb", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        HERB = os.path.join(CountyDataGDB, county + "_Herb")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("Turf 2 took " + str((time.clock() - time_start) / 60) + " minutes")

    # TURF 3: Identify Potential Rural Turf Based on Proximity to Development
    # Skipping this because we are going with Worldview turf

    # TURF 4: Create Parcel-based Turf and Fractional Turf Masks
    if arcpy.Exists(PARCELS):
        # TURF 4a: Check projection of parcel data and reproject if needed
        time_start = time.clock()
        P1 = arcpy.Describe(PARCELS).spatialReference
        P2 = arcpy.Describe(IR).spatialReference
        if arcpy.Exists(county + "_ParcelsAlb"):
            PARCELS = os.path.join(CountyDataGDB, county + "_ParcelsAlb")
            arcpy.AddMessage("Projected parcel data exists")
        elif P1 == P2:
            arcpy.Rename_management(PARCELS, county + "_ParcelsAlb")
            PARCELS = os.path.join(CountyDataGDB, county + "_ParcelsAlb")
            arcpy.AddMessage("Parcel projection correct and dataset renamed")
        else:
            arcpy.Project_management(PARCELS, county + "_ParcelsAlb", IR)
            PARCELS = os.path.join(CountyDataGDB, county + "_ParcelsAlb")
            arcpy.AddMessage("Parcel data reprojected to Albers")
        arcpy.AddMessage("Turf 4a took " + str((time.clock() - time_start) / 60) + " minutes")

        # TURF 4b: Create Turf Parcels
        # Skipping this because we are going with Worldview turf

        # TURF 4c: Create Fractional Turf Parcels
        time_start = time.clock()
        arcpy.Select_analysis(PARCELS, county + "_Parcels_FTGtemp", 'ACRES2 > 10')
        Zstat = ZonalStatisticsAsTable(county + "_Parcels_FTGtemp", "UNIQUEID", INR, "Parcel_IMP2", "DATA", "SUM")
        arcpy.JoinField_management(county + "_Parcels_FTGtemp", "UNIQUEID", "Parcel_IMP2", "UNIQUEID", ["SUM"])
        arcpy.AddField_management(county + "_Parcels_FTGtemp", "PCT_IMP", "DOUBLE", "", "", "", "", "NULLABLE",
                                  "NON_REQUIRED", "")
        arcpy.AddField_management(county + "_Parcels_FTGtemp", "VALUE", "SHORT", "", "", "", "", "NULLABLE",
                                  "NON_REQUIRED", "")
        arcpy.CalculateField_management(county + "_Parcels_FTGtemp", "VALUE", "1", "PYTHON_9.3", "")
        arcpy.CalculateField_management(county + "_Parcels_FTGtemp", "PCT_IMP",
                                        "min([!VALUE!,((!SUM!/4046.86)/!ACRES2!)])", "PYTHON_9.3")
        arcpy.Select_analysis(county + "_Parcels_FTGtemp", county + "_Parcels_FTG", 'PCT_IMP >= 0.1')
        arcpy.FeatureToRaster_conversion(county + "_Parcels_FTG", "VALUE", county + "_FTG_parcels", 1)
        FTGparcels = os.path.join(CountyDataGDB, county + "_FTG_parcels")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("Turf 4c took " + str((time.clock() - time_start) / 60) + " minutes")

        # TURF 4d: Mosaic available overlays to create Turf Mask with parcels
        time_start = time.clock()
        inrasList = []
        if arcpy.Exists(ROW):
            inrasList.append(ROW)
        if arcpy.Exists(INST):
            inrasList.append(INST)
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasList))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_TGmask", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("Turf 4d took " + str((time.clock() - time_start) / 60) + " minutes")

        # TURF 4e: Mosaic available overlays to create FTG Mask with parcels
        time_start = time.clock()
        inrasList = []
        if arcpy.Exists(FTG_LU):
            inrasList.append(FTG_LU)
        if arcpy.Exists(FEDS):
            inrasList.append(FEDS)
        if arcpy.Exists(FTGparcels):
            inrasList.append(FTGparcels)
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasList))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_FTGmask", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("Turf 4e took " + str((time.clock() - time_start) / 60) + " minutes")

    else:
        # TURF 5a: Mosaic available overlays to create Turf Mask without parcels
        time_start = time.clock()
        inrasList = []
        if arcpy.Exists(ROW):
            inrasList.append(ROW)
        if arcpy.Exists(INST):
            inrasList.append(INST)
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasList))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_TGmask", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("Turf 5a took " + str((time.clock() - time_start) / 60) + " minutes")

        # TURF 5b: Mosaic available overlays to create FTG Mask without parcels
        time_start = time.clock()
        inrasList = []
        if arcpy.Exists(FTG_LU):
            inrasList.append(FTG_LU)
        if arcpy.Exists(FEDS):
            inrasList.append(FEDS)
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasList))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_FTGmask", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("Turf 5b took " + str((time.clock() - time_start) / 60) + " minutes")

    # TURF 6: Extract Herbaceous within Turf Mask and Reclass
    time_start = time.clock()
    outExtractByMask = ExtractByMask(county + "_Herb", county + "_TGmask")
    outExtractByMask.save(county + "_TURFtemp", )
    outSetNull = SetNull(county + "_TURFtemp", "13",
                         "VALUE = 0")  # If the value == 0, make it null, if the value is != 0, make it 13
    outSetNull.save(county + "_TG_1m_no_worldview_turf")
    arcpy.AddMessage("Turf 6 took " + str((time.clock() - time_start) / 60) + " minutes")

    # TURF 6b: Mosaic herb with worldview class 71
    time_start = time.clock()
    worldview_reclass = Reclassify(county + "_LaCoTC", "Value", RemapValue([[71, 13]]), "NODATA")
    worldview_reclass.save(county + "_WV_TURF")
    rasLocation = Output1mGDB
    inrasList = []
    inrasList.append(county + "_TG_1m_no_worldview_turf")
    inrasList.append(county + "_WV_TURF")
    inrasList = str(";".join(inrasList))
    arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_TG_1m", "", "4_BIT", "1", "1", "LAST",
                                       "FIRST")
    arcpy.AddMessage("Turf 6b took " + str((time.clock() - time_start) / 60) + " minutes")

    # FRAC 1: Extract Herbaceous within FTG Mask and Reclass
    time_start = time.clock()
    outExtractByMask = ExtractByMask(HERB, county + "_FTGmask")
    outExtractByMask.save(county + "_FTGtemp", )
    outSetNull = SetNull(county + "_FTGtemp", "11", "VALUE = 0")
    outSetNull.save(os.path.join(Output1mGDB, county + "_FTG_1m"))
    arcpy.AddMessage("Frac 1 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FRAC 2: Extract Herbaceous within FINR Mask and Reclass
    time_start = time.clock()
    if arcpy.Exists(FINR_LU):
        try:
            arcpy.CalculateStatistics_management(FINR_LU)
            outExtractByMask = ExtractByMask(HERB, FINR_LU)
            outExtractByMask.save(county + "_FINRtemp", )
            outSetNull = SetNull(county + "_FINRtemp", "12",
                                 "VALUE = 0")  # If the value == 0, make it null, if the value is != 0, make it 12
            outSetNull.save(os.path.join(Output1mGDB, county + "_FINR_1m"))
            arcpy.AddMessage("Fractional INR mask complete and...")
        except:
            arcpy.AddMessage("Fractional INR mask is null and...")
    else:
        arcpy.AddMessage("--- FRAC #2 Fractional INR Mask is Missing ---")
    arcpy.AddMessage("Frac 2 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FRAC 3: Cleanup
    time_start = time.clock()
    arcpy.Delete_management(county + "Parcel_IMP")
    arcpy.Delete_management(county + "Parcel_IMP2")
    arcpy.Delete_management(county + "_RTmask")
    arcpy.Delete_management(county + "_Parcels_TURFtemp")
    arcpy.Delete_management(county + "_Parcels_TURF")
    arcpy.Delete_management(county + "_TURF_parcels")
    arcpy.Delete_management(county + "_Parcels_FTGtemp")
    arcpy.Delete_management(county + "_Parcels_FTG")
    arcpy.Delete_management(county + "_FTG_parcels")
    arcpy.Delete_management(county + "_TGmask")
    arcpy.Delete_management(county + "_FTGmask")
    arcpy.Delete_management(county + "_TURFtemp")
    arcpy.Delete_management(county + "_FTGtemp")
    arcpy.Delete_management(county + "_FINRtemp")
    arcpy.Delete_management(county + "_TG_1m_no_worldview_turf")
    arcpy.Delete_management(county + "_WV_TURF")
    arcpy.AddMessage("Frac 3 took " + str((time.clock() - time_start) / 60) + " minutes")

    ## FOREST MODEL
    # This model uses the following:
    # DEV113, DEV37, DEV27, DEV18, TC

    # FOR 0.1: Cleanup
    time_start = time.clock()
    arcpy.Delete_management(county + "_RLTCP")
    arcpy.Delete_management(county + "_EDGE")
    arcpy.Delete_management(county + "_CDEdge")
    arcpy.Delete_management(county + "_URBmask")
    arcpy.Delete_management(county + "_RURmask")
    arcpy.Delete_management(county + "_CDEdge")
    arcpy.Delete_management(county + "_URB_TCT")
    arcpy.Delete_management(county + "_RUR_TCT")
    arcpy.Delete_management(county + "_TCT1")
    arcpy.Delete_management(county + "_nonTCT")
    arcpy.Delete_management(county + "_potFOR")
    arcpy.Delete_management(county + "_NATnhbrs")
    arcpy.Delete_management(county + "_ForRG")
    arcpy.Delete_management(county + "_MOtemp")
    arcpy.Delete_management(county + "_MOspace")
    arcpy.Delete_management(county + "_MOherb")
    arcpy.Delete_management(county + "_MOTrees")
    arcpy.AddMessage("FOR 0.1 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 1: Identify Rural Core Areas of Tree Canopy over Pervious Surfaces
    time_start = time.clock()
    RLTCP = Int(SetNull(Con(IsNull(DEV113), 1) * TC <= 0, Con(IsNull(DEV113), 1) * TC))
    RLTCP.save(county + "_RLTCPTemp")
    arcpy.CopyRaster_management(county + "_RLTCPTemp", county + "_RLTCP", "", "0", "0", "", "", "4_BIT", "", "", "", "")
    arcpy.Delete_management(county + "_RLTCPTemp")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 1 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 2: Define interface between Rural Core Areas and Edges of Developed Areas
    time_start = time.clock()
    EDGE = Int(SetNull(Con(IsNull(DEV27), 1, 0) * TC <= 0, Con(IsNull(DEV27), 1, 0) * TC))
    EDGE.save(county + "_EDGETemp")
    arcpy.CopyRaster_management(county + "_EDGETemp", county + "_EDGE", "", "0", "0", "", "", "4_BIT", "", "", "", "")
    arcpy.Delete_management(county + "_EDGETemp")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 2 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 3: Bleed/Expand Rural Core Areas to Edge of Developed Areas
    time_start = time.clock()
    outCostDistance = CostDistance(county + "_RLTCP", county + "_EDGE", "", "", "", "", "", "")
    outCostDistance.save(county + "_CDEdge")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 3 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 4: Create Tree Canopy over Turf Grass Masks
    time_start = time.clock()
    UrbMask = Int(Con(IsNull(county + "_CDEdge"), 1) * DEV37)
    UrbMask.save(county + "_URBmask")
    RurMask = Int(Con(IsNull(county + "_URBmask"), 1))
    RurMask.save(county + "_RURmask")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 4 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 5: Rural and Urban TCT
    time_start = time.clock()
    RurTCT = Int(Raster(county + "_RURmask") * TC * DEV18)  # Limits extent of tree canopy in rural areas
    RurTCT.save(county + "_RUR_TCT")
    outTimes = Raster(county + "_URBmask") * TC
    outTimes.save(county + "_URB_TCT")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 5 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 6: Final TCT (Mosaic to New Raster)
    time_start = time.clock()
    rasLocation = CountyDataGDB
    inRasters = Raster(county + "_URB_TCT"), Raster(county + "_RUR_TCT")
    arcpy.MosaicToNewRaster_management(inRasters, rasLocation, county + "_TCT1", "", "4_BIT", "1", "1", "LAST", "FIRST")
    outReclassify = Con(Raster(county + "_TCT1") == 1, 9)
    outReclassify.save(os.path.join(Output1mGDB, county + "_TCT_1m"))
    TCT = os.path.join(Output1mGDB, county + "_TCT_1m")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 6 took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR 7: Identify Potential Forests
    time_start = time.clock()
    NonTCT = Int(Con(IsNull(TCT), 1))
    NonTCT.save(county + "_nonTCT")
    outTimes1 = TC * Raster(county + "_nonTCT")
    outTimes1.save(county + "_potFOR")
    arcpy.Delete_management("in_memory")
    arcpy.AddMessage("FOR 7 took " + str((time.clock() - time_start) / 60) + " minutes")

    ## WETLAND MODEL
    # Skipping this because we already have the wetlands done

    # FOR 8: Separate Mixed Open Trees from Potential Forests considering adjacent natural land uses
    time_start = time.clock()
    WLF = os.path.join(Output1mGDB, county + "_WLF_1m")
    WLO = os.path.join(Output1mGDB, county + "_WLO_1m")
    WLT = os.path.join(Output1mGDB, county + "_WLT_1m")
    outCon = Con(Raster(WAT) == 3, 1)
    outCon.save(county + "_watFOR")

    WAT_FOR = os.path.join(CountyDataGDB, county + "_watFOR")
    POT_FOR = os.path.join(CountyDataGDB, county + "_potFOR")

    inrasList = []
    if arcpy.Exists(WLT):
        inrasList.append(WLT)
    if arcpy.Exists(WLF):
        inrasList.append(WLF)
    if arcpy.Exists(WLO):
        inrasList.append(WLO)
    if arcpy.Exists(WAT_FOR):
        inrasList.append(WAT_FOR)
    if arcpy.Exists(POT_FOR):
        inrasList.append(POT_FOR)

    inrasList = str(";".join(inrasList))  # delimit by ";"
    rasLocation = os.path.join(CountyDataGDB)
    arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_NATnhbrs", "", "4_BIT", "1", "1", "LAST",
                                       "FIRST")
    outRegionGrp = RegionGroup(Raster(county + "_NATnhbrs"), "EIGHT", "WITHIN", "NO_LINK", "0")
    outRegionGrp.save(county + "_ForRG")
    outCon = Con(county + "_ForRG", 1, "", "VALUE > 0 AND COUNT >= 4047")
    outExtractByMask = ExtractByMask(TC, outCon)
    outCon2 = Con(outExtractByMask == 1, 8)
    outCon2.save(os.path.join(Output1mGDB, county + "_FOR_1m"))
    outCon3 = Con(county + "_ForRG", 1, "", "VALUE > 0 AND COUNT < 4047")
    outExtractByMask = ExtractByMask(TC, outCon3)
    outExtractByMask.save(county + "_MOTrees")
    arcpy.Delete_management("in_memory")

    arcpy.AddMessage("FOR 8 took " + str((time.clock() - time_start) / 60) + " minutes")

    ## MIXED OPEN MODEL
    # This model uses the following:
    # BAR, BEACH, M_LANDUSE, LV, MINE, SS, TREES

    # MO 1: Create Mixed Open with just MOtrees and Scrub-shrub (no ancillary data)
    time_start = time.clock()

    inrasListMO = []
    if arcpy.Exists(BEACH):
        inrasListMO.append(BEACH)
    if arcpy.Exists(M_LANDUSE):
        inrasListMO.append(M_LANDUSE)
    if arcpy.Exists(MINE):
        inrasListMO.append(MINE)

    if not inrasListMO:
        start_time = time.time()
        inrasList = []
        if arcpy.Exists(TREES):
            inrasList.append(TREES)
        if arcpy.Exists(SS):
            inrasList.append(SS)
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasList))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_MOtemp", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        outSetNull = SetNull(county + "_MOtemp", "10", "VALUE = 0")
        outSetNull.save(os.path.join(Output1mGDB, county + "_MO_1m"))
        arcpy.Delete_management("in_memory")

        arcpy.AddMessage("MO 1 took " + str((time.clock() - time_start) / 60) + " minutes")

    else:
        # MO 2: Create Mixed Open with Ancillary Data
        # MO 2a: Create Potential Mixed Open Area
        time_start = time.clock()
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasListMO))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_MOspace", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("MO 2a took " + str((time.clock() - time_start) / 60) + " minutes")

        # MO2b: Create Herbaceous Layer
        time_start = time.clock()
        if arcpy.Exists(county + "_Herb"):
            HERB = os.path.join(CountyDataGDB, county + "_Herb")
            print("Herbaceous Layer Exists")
        else:
            start_time = time.time()
            rasLocation = CountyDataGDB
            inRasters = Raster(BAR), Raster(LV)
            arcpy.MosaicToNewRaster_management(inRasters, rasLocation, county + "_Herb", "", "4_BIT", "1", "1", "LAST",
                                               "FIRST")
            HERB = os.path.join(CountyDataGDB, county + "_Herb")
            arcpy.Delete_management("in_memory")
        arcpy.AddMessage("MO 2b took " + str((time.clock() - time_start) / 60) + " minutes")

        # MO 2c: Extract Herbaceous within MOspace
        time_start = time.clock()
        inRaster = Raster(HERB)
        inMaskData = Raster(county + "_MOspace")
        outExtractByMask = ExtractByMask(inRaster, inMaskData)
        outExtractByMask.save(county + "_MOherb")
        MOherb = os.path.join(CountyDataGDB, county + "_MOherb")
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("MO 2c took " + str((time.clock() - time_start) / 60) + " minutes")

        # MO 2d: Final Mixed Open (mosaic)
        time_start = time.clock()
        inrasList = []
        if arcpy.Exists(TREES):
            inrasList.append(TREES)
        if arcpy.Exists(SS):
            inrasList.append(SS)
        if arcpy.Exists(MOherb):
            inrasList.append(MOherb)
        rasLocation = CountyDataGDB
        inrasList = str(";".join(inrasList))  # delimit by ";"
        arcpy.MosaicToNewRaster_management(inrasList, rasLocation, county + "_MOtemp", "", "4_BIT", "1", "1", "LAST",
                                           "FIRST")
        outSetNull = SetNull(county + "_MOtemp", "10", "VALUE = 0")
        outSetNull.save(os.path.join(Output1mGDB, county + "_MO_1m"))
        arcpy.Delete_management("in_memory")
        arcpy.AddMessage("MO 2d took " + str((time.clock() - time_start) / 60) + " minutes")

    # FOR/MO Cleanup
    time_start = time.clock()
    arcpy.Delete_management(county + "_RLTCP")
    arcpy.Delete_management(county + "_EDGE")
    arcpy.Delete_management(county + "_CDEdge")
    arcpy.Delete_management(county + "_URBmask")
    arcpy.Delete_management(county + "_RURmask")
    arcpy.Delete_management(county + "_CDEdge")
    # arcpy.Delete_management(county + "_URB_TCT")
    # arcpy.Delete_management(county + "_RUR_TCT")
    # arcpy.Delete_management(county + "_TCT1")
    arcpy.Delete_management(county + "_nonTCT")
    arcpy.Delete_management(county + "_potFOR")
    arcpy.Delete_management(county + "_NATnhbrs")
    arcpy.Delete_management(county + "_ForRG")
    arcpy.Delete_management(county + "_MOtemp")
    arcpy.Delete_management(county + "_MOspace")
    arcpy.Delete_management(county + "_MOherb")
    arcpy.AddMessage("FOR/MO took " + str((time.clock() - time_start) / 60) + " minutes")

    ## FINAL AGGREGATION MODEL
    # Final 2: Reclass Input Rasters to Appropriate Mosaic Hierarchical Values
    time_start = time.clock()
    INR2 = Con(Raster(INR) == 1, 2)
    TCI2 = Con(Raster(TCI) == 1, 3)
    WAT2 = Con(Raster(WAT) == 1, 4)
    if arcpy.Exists(WLT):
        WLT2 = Con(Raster(WLT) == 1, 5)
    if arcpy.Exists(WLF):
        WLF2 = Con(Raster(WLF) == 1, 6)
    if arcpy.Exists(WLO):
        WLO2 = Con(Raster(WLO) == 1, 7)
    if arcpy.Exists(CRP):
        CRP2 = Con(Raster(CRP) == 1, 14)
    if arcpy.Exists(PAS):
        PAS2 = Con(Raster(PAS) == 1, 15)
    arcpy.AddMessage("Final 2 took " + str((time.clock() - time_start) / 60) + " minutes")

    # Final 3: Mosaic All 1m Rasters
    time_start = time.clock()
    LUlist = []
    if arcpy.Exists(IR):
        LUlist.append(IR)
    if arcpy.Exists(INR2):
        LUlist.append(INR2)
    if arcpy.Exists(TCI2):
        LUlist.append(TCI2)
    if arcpy.Exists(WAT2):
        LUlist.append(WAT2)
    if arcpy.Exists(WLT):  # use WLT because WLT2 is only defined if WLT exists
        LUlist.append(WLT2)
    if arcpy.Exists(WLF2):
        LUlist.append(WLF2)
    if arcpy.Exists(WLO2):
        LUlist.append(WLO2)
    if arcpy.Exists(FOR):
        LUlist.append(FOR)
    if arcpy.Exists(TCT):
        LUlist.append(TCT)
    if arcpy.Exists(MO):
        LUlist.append(MO)
    if arcpy.Exists(FTG):
        LUlist.append(FTG)
    if arcpy.Exists(FINR):
        LUlist.append(FINR)
    if arcpy.Exists(TG):
        LUlist.append(TG)
    if arcpy.Exists(CRP2):
        LUlist.append(CRP2)
    if arcpy.Exists(PAS2):
        LUlist.append(PAS2)

    # Final 4: Split Mosaic and Reclass Land Uses to [1,0]
    rasLocation = CountyDataGDB
    outCellStats = CellStatistics(LUlist, "MINIMUM",
                                  "DATA")  # LUlist must be used directly as inRasters because it has the correct format needed for CellStatistics, else 000732 error.
    arcpy.Delete_management(county + "_Mosaic")
    outCellStats.save(county + "_Mosaic")
    arcpy.Delete_management("in_memory")

    arcpy.AddMessage("Final 3 and 4 took " + str((time.clock() - time_start) / 60) + " minutes")
    arcpy.AddMessage("Going to loop and try the next county.")
    continue

    # Final 5: Combine all 10m rasters (8-10 minutes)
    time_start = time.clock()

    arcpy.AddMessage("Final 5 took " + str((time.clock() - time_start) / 60) + " minutes")

    # Final 6: Rename, Create, and Calcualte Fields
    time_start = time.clock()

    arcpy.AddMessage("Final 6 took " + str((time.clock() - time_start) / 60) + " minutes")

    # Final 7: Create Final Phase 6 Rasters in a Geodatabase (necessary first step) and convert to TIFFs
    time_start = time.clock()

    arcpy.AddMessage("Final 7 took " + str((time.clock() - time_start) / 60) + " minutes")














