# Phase 6 Land Use Conversion Model - Virginia

##Folder structure

```

[GDB] Resources.gdb (Global, available to all county folders)
|-- Phase6_Snap
|-- Stream

[DIR] COUNTY_FIPSCODE
|
|--[GDB] Data (Geodatabase for storing model resources)
|    |-- TC      (Worldview classes 41, 42, 43, 61, all 100 classes except for 101, 121, 122)
|    |-- LV      (Worldview classes 71, 81, 82, 171, 181, 182)
|    |-- Barren  (Worldview classes 31, 131)
|    |-- Other land use classes (e.g. MOBeach, DEV18/27/37/113, FedPark, TurfNT...)
|
|--[DIR] Temp (Directory for storing intermediate geodatabase files)
|    |--[GDB] TEMP_1m.gdb  (Geodatabase for storing intermediate files related to 1m rasters)
|    |--[GDB] TEMP_10m.gdb (Geodatabase for storing intermediate files related to 10m rasters)
|
|--[DIR] Outputs (Directory for storing final geodatabase files)
|    |--[GDB] Final_1m.gdb  (Geodatabase for storing final 1m rasters. All of the following exist at the start of the model, except possible the wetlands rasters)
|    |    |-- IR_1m
|    |    |-- INR_1m
|    |    |-- TCoI_1m
|    |    |-- WLT_1m
|    |    |-- WLF_1m
|    |    |-- WLO_1m
|    |    |-- PAS_1m   (Worldview class 81)
|    |    |-- CRO_1m   (Worldview class 82)
|    |    
|    |--[GDB] Final_10m.gdb (Geodatabase for storing final files 10m rasters)
|    |--[DIR] Final_Tifs  (Directory for storing final 10m tifs)

