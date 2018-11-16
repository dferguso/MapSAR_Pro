#-------------------------------------------------------------------------------
# Name:        UpdateLayout.py
# Purpose: Updates the following fields on the map layout: UTM Zone, USNG 100k
#  Zone and Magnestic Declination (from Incident Information Layer).
#
# Author:      Don Ferguson
#
# Created:     06/18/ 2012
# Copyright:   (c) Don Ferguson 2012
# Licence:
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The GNU General Public License can be found at
#  <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# Take courage my friend help is on the way
try:
    arcpy
except NameError:
    import arcpy
from arcpy import env
try:
    sys
except NameError:
    import sys
from os import path
from math import atan, tan, sin
from geomag import declination

# Overwrite pre-existing files
env.overwriteOutput = True

global wrkspc 
wrkspc= env.workspace
global wrkFldr 
wrkFldr= path.dirname(wrkspc)


def getMap():
    ## Get current aprx and map
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT");df = aprx.listMaps()[0]
        return(aprx,df)
    except SystemExit as err:
        pass

def checkFields(fc, fldName, fldType):
    desc=arcpy.Describe(fc)
    # Get a list of field names from the feature
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    if fldName not in field_names:
        arcpy.AddField_management (fc, fldName, fldType)
    return

def gNorth_Check(fc, fldName, fldType):
    checkFields(fc, fldName, fldType)
    arcpy.CalculateGridConvergenceAngle_cartography(fc,fldName, "GEOGRAPHIC")
    return
    
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)
    
def updateMapLayout(aprx, df, lyt, mf):    
    fc1 = "Planning_Points"
    fc2 = "Incident_Info"
    fc3 = "AssetPts"
    
    IncidPP = path.join(wrkspc, fc1)
    desc=arcpy.Describe(IncidPP)
    dfSpatial_Ref=desc.spatialReference.name
    dfSpatial_Type = desc.spatialReference.type
    
    # Get UTM and USNG Zones
    # Get declination from Incident Information

    cPlanPt = arcpy.GetCount_management(fc1)
    cBasePt = arcpy.GetCount_management(fc3)
    if int(cPlanPt.getOutput(0)) > 0:
        cPlanPt = cPlanPt
        intLyr = "Incident\Planning_Points"
    elif int(cBasePt.getOutput(0)) > 0:
        cPlanPt = cBasePt
        fc1 = fc3
        intLyr = "Assets\Assets"
    else:
        arcpy.AddError("Warning: Need to add Planning Point or ICP prior to updating map layout.\n")
        arcpy.AddError("Warning: Map Layout COULD NOT be updated.\n")
        sys.exit(0)

    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    shapefieldname = desc.ShapeFieldName

    # Determine grid North (if applicable) and declination 
    fld_gNorth = "gNORTH"
    field_type = "FLOAT"
    if fc1 == "Assets":
        where0 = '"Asset_Type" = 1'
    else:
        where0 = ""
        
    if dfSpatial_Type=="Projected":
        cMeridian=desc.spatialReference.centralmeridian
    gridConv = []
    deClinat=[]
    for row in arcpy.da.SearchCursor(fc1,["SHAPE@XY"],where0,unProjCoordSys):
        x,y=row[0]
        if dfSpatial_Type=="Projected":
            gridConv.append(atan(tan(x-cMeridian)+sin(y)))
        else:
            gridConv.append(0.0)
        deClinat.append(declination(y,x))
    
    # Grid North determination
    gridNorth=mean(gridConv)
    gridN = round(gridNorth,2)
    if gridN > 0:
        gCard ="W"
    else:
        gCard ="E"
    gNorthTxt = str(abs(gridN)) + " " + gCard
    arcpy.AddMessage('Grid North: {0}'.format(gNorthTxt))
    
    # Magnetic Declination
    declin = mean(deClinat)
    MagDeclinlination = round(declin,2)
    if MagDeclinlination < 0:
        Cardinal ="W"
    else:
        Cardinal ="E"
    MagDecTxt = str(abs(MagDeclinlination)) + " " + Cardinal    
    

    # Rotate data frame to adjust map layout for True North vs Grid North.
    # Grid North is parallel with the edge of the page.  The "True North" arrow
    # should be rotated to TRUE NORTH.
    
    # Rotate the map by grid north - or do I need to rotate to -gridN?
    mf.camera.heading=gridN
    try:
        if lyt.listElements('TEXT_ELEMENT','MagDec'):
            magNorth = lyt.listElements('TEXT_ELEMENT','MagDec')[0]
            magNorth.text = MagDecTxt
        if lyt.listElements('TEXT_ELEMENT','gNorth'):
            gNorth = lyt.listElements('TEXT_ELEMENT','gNorth')[0]
            gNorth.text = gNorthTxt
    except:
        pass

##    try:  #Update Incident Name and Number with the file name and dataframe name
    IncidName = " "
    IncNum = " "
    flds = ['IncidName', 'IncidNum']
    with arcpy.da.SearchCursor(fc2, flds) as cursor:
        for row in cursor:
            IncidName=row[0]
            IncNum = row[1]    
    arcpy.AddMessage("\nThe Incident Name is " + IncidName)
    arcpy.AddMessage("The Incident Number is: " + IncNum + "\n")
    if lyt.listElements("TEXT_ELEMENT", "MapTitle"):
        MapTitle=lyt.listElements("TEXT_ELEMENT", "MapTitle")[0]
        MapTitle.text = " "

    if lyt.listElements("TEXT_ELEMENT", "RefNum"):
        RefNum=lyt.listElements("TEXT_ELEMENT", "RefNum")[0]
        RefNum.text = " "

    del cursor, row
    del IncidName, IncNum, flds
##    except:
##        arcpy.AddMessage("Error: Update Incident Name and Number manually\n")

    arcpy.AddMessage("Grid North correction to True North based on location of IPP or ICP is: {0}".format(gNorthTxt))
#    try:
    cIncident=arcpy.GetCount_management(fc2)
    # Get list of fields in Incident Information
    fieldList = arcpy.ListFields(fc2)
    field=[]
    for fld in fieldList:
        field.append(fld.name.encode('ascii','ignore'))

    fld2 = "MapDatum"
    fld3 = "MapCoord"        

    incdFlds=["MagDec","gNorth", "UTM_ZONE", "USNG_GRID", "MapDatum"]#,fld2, fld3]
    if int(cIncident.getOutput(0)) > 0:
        with arcpy.da.UpdateCursor(fc2, incdFlds) as cursor:
            for row in cursor:
                row[0]=MagDecTxt
                row[1]=gNorthTxt
#                row[2]=UTMZn.text
#                row[3]=USNGZn.text
#                row[4]=dfSpatial_Ref
                cursor.updateRow(row)
        del cursor, row
    else:
        arcpy.AddWarning("No Incident Information provided\n")
#    except:
#        arcpy.AddMessage("Error: Update Magnetic Declination Manually\n")       
    return


###########Main############
if __name__ == '__main__':
    aprx, df = getMap()
    getLayout = arcpy.GetParameterAsText(0)
    getFrame = arcpy.GetParameterAsText(1)
    # Get layouts and map frames
    # test
    gLayout=[]
    for lyt in aprx.listLayouts():
        gLayout.append(lyt.name)
        print(lyt.name)
    indLayout = gLayout.index(getLayout)
    lyt=aprx.listLayouts()[indLayout]
    mFrame=[]
    for ele in lyt.listElements('MAPFRAME_ELEMENT'):
        mFrame.append(ele.name)
        print(ele.name)
    # Just use the [0] mapframe
    mf=lyt.listElements('MAPFRAME_ELEMENT')[0]
        
    updateMapLayout(aprx, df, lyt, mf)
