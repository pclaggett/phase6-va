# Phase 6 Land Use Conversion Model - Virginia

##Folder structure

```

[GDB] Resources.gdb (Global, available to all county folders)
|-- Snap
|-- Stream

[DIR] COUNTY
|
|--[DIR] COUNTY_P6_Temp (Folder for storing intermediate geodatabase files)
|    |--[GDB] COUNTY_1m.gdb  (Geodatabase for storing intermediate files related to 1m rasters)
|    |--[GDB] COUNTY_10m.gdb (Geodatabase for storing intermediate files related to 10m rasters)
|
|--[GDB] COUNTY_P6_Resources (Geodatabase for storing model resources)
|    |-- TC      (Worldview classes 41, 42, 43, 61, all 100 classes except for 101, 121, 122)
|    |-- LV      (Worldview classes 71, 81, 82, 171, 181, 182)
|    |-- Barren  (Worldview classes 31, 131)
|    |-- Other land use classes (e.g. MOBeach, DEV18/27/37/113, FedPark, TurfNT...)
|
|--[DIR] COUNTY_P6_Outputs (Folder for storing final geodatabase files)
|    |--[GDB] COUNTY_Final_1m.gdb  (Geodatabase for storing final 1m rasters)
|    |    |-- IR_1m
|    |    |-- INR_1m
|    |    |-- TCoI_1m
|    |    |-- WLT_1m
|    |    |-- WLF_1m
|    |    |-- WLO_1m
|    |    |-- PAS_1m   (Worldview class 81)
|    |    |-- CRO_1m   (Worldview class 82)
|    |    
|    |--[GDB] COUNTY_Final_10m.gdb (Geodatabase for storing final files 10m rasters)
|    |--[DIR] COUNTY_Final_Tifs  (Directory for storing final 10m tifs)

```

## Model outline

```
## Environments
Working directory  --> COUNTY_P6_Temp/COUNTY_P6_Resources
Scratch directory  --> COUNTY_P6_Temp/COUNTY_1m.gdb
Snap raster        --> COUNTY_Final_1m.gdb/IR_1m

############# TURF MODEL #############
## TURF 1: Mosaic All Non-raod Impervious Surfaces
## TURF 2: Create Herbaceous Layer
-- OMITTED -- ## TURF 3: Identify Potential Rural Turf Based on Proximity to Development
## TURF 4: Create Parcel-based Turf and Fractional Turf Masks
## TURF 4a: Check projection of parcel data and reproject if needed
-- OMITTED -- ## TURF 4b: Create Turf Parcels
## TURF 4c: Create Fractional Turf Parcels
## TURF 4d: Mosaic available overlays to create Turf Mask with parcels
   ++ ADJUSTMENT ++  Include only RoW and INST
## TURF 4e: Mosaic available overlays to create FTG Mask with parcels
## TURF 5a: Mosaic available overlays to create Turf Mask without parcels
## TURF 5b: Mosaic available overlays to create FTG Mask without parcels
## TURF 6: Extract Herbaceous within Turf Mask and Reclass
++ ADDED STEP ++ ## TURF 6b: Mosaic this output with Worldview class 71 to create VA TG_1m
## FRAC 1: Extract Herbaceous within FTG Mask and Reclass
## FRAC 2: Extract Herbaceous within FINR Mask and Reclass

############ FOREST MODEL ############
## FOR 1: Identify Rural Core Areas of Tree Canopy over Pervious Surfaces
## FOR 2: Define interface between Rural Core Areas and Edges of Developed Areas
## FOR 3: Bleed/Expand Rural Core Areas to Edge of Developed Areas
## FOR 4: Create Tree Canopy over Turf Grass Masks
## FOR 5: Rural and Urban TCT
## FOR 6: Final TCT (Mosaic to New Raster)
## FOR 7: Identify Potential Forests
--- OMITTED WETLAND SUBMODEL ---
## FOR 8: Separate Mixed Open Trees from Potential Forests considering adjacent natural land uses

########## MIXED OPEN MODEL ##########
## MO 1: Create Mixed Open with just MOtrees and Scrub-shrub (no ancillary data)
## MO 2: Create Mixed Open (If ancillary data is present)
## MO 2a: Create Potential Mixed Open Area
## MO 2b: Create Herbaceous Layer
## MO 2c: Extract Herbaceous within MOspace.
## MO 2d: Final Mixed Open (mosaic)

######### AGGREGATION MODEL ##########
## Final 2: Reclass Input Rasters to Appropriate Mosaic Hierarchical Values.
   ++ ADJUSTMENT ++ Remove CDL and AG rasters and add Cropland and Pasture
## Final 3: Mosaic All 1m Rasters
## Final 4: Split Mosaic and Reclass Land Uses to [1,0]

## Change environments
Working directory  --> COUNTY_P6_Temp/COUNTY_10m.gdb
Scratch directory  --> COUNTY_P6_Temp/COUNTY_10m.gdb
Snap raster        --> County_P6_Resources.gdb/Snap

## Final 5: Combine all 10m rasters
## Final 6: Rename, Create, and Calcualte Fields
## Final 7: Create Final Phase 6 Rasters in a Geodatabase (necessary first step) and convert to TIFFs


```