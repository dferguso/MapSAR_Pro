#-------------------------------------------------------------------------------
# Name:       NewIncident.py
# Purpose: Create a new Incident for IGT4SAR and Project in the correct
#  coordinate system.
#
# Author:      Don Ferguson
#
# Created:     02/18/2013
# Copyright:   (c) Don Ferguson 2013
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
try:
    arcpy
except NameError:
    import arcpy
from arcpy import env
try:
    sys
except NameError:
    import sys
import uuid   
from datetime import datetime
from os import path, listdir
# from errno import ENOTDIR
from shutil import copyfile#, copytree, copy
##import traceback

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

def getMap():
    ## Get current aprx and map
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT");df = aprx.listMaps()[0]
        return(aprx,df)
    except SystemExit as err:
        pass

def checkDomain(wrkspc, domName, keyName):
    domains=arcpy.da.ListDomains(wrkspc)
    for dom in domains:
        if dom.name==domName:
            if dom.domainType=='CodedValue':
                coded_values = dom.codedValues
                if keyName in coded_values.keys():
                    return True
                else:
                    return False
    
def checkForm(out_fc, TAF2Use):
    icsFile=[]
    formsDir = 'C:\\MapSAR_Pro\\Forms\\TAF_ICS204'
    icsPath=path.join(formsDir,"ICS204Forms_Available.txt")
    ics204={}
    if path.isfile(icsPath):
        with open(icsPath)as f:
            for line in f:
                (key, val) = line.split(',',1)
                ics204[key]= val.strip()
        icsFile.append(ics204[TAF2Use])
    else:
        icsFile.append("Default_204Form_pg1.pdf")

    formList=list(ics204.keys())
    try:
        del(formList[formList.index('Default')])
        newList=sorted(formList)
        formList = ['Default'] + newList
    except:
        pass

    (FName,FType)= icsFile[0].split('.')

    if 'pg1' in FName:
        icsFile=[]
        [icsFile.append(f) for f in listdir(formsDir) if FName[:-3] in f]

    output = path.join(out_fc, "Assignments")
    for icsFileX in icsFile:
        if not icsFileX in listdir(output):
            formFile = path.join(formsDir, icsFileX)
            destFile = path.join(output, icsFileX)
            if icsFileX in listdir(formsDir):
                arcpy.AddMessage("\nForm {0} added to folder {1}.".format(icsFileX, output))
                copyfile(formFile, destFile)
            else:
                arcpy.AddError("{0} is not available, please check {1} or {2} for correct form".format(icsFileX, output, formsDir))
                sys.exit(1)
    return(formList)

def geoCoords(geoUnits):
    newPt=geoUnits.split(',')
    xCoord=newPt[0].strip()
    yCoord=newPt[1].strip()
    return('{0},{1}'.format(yCoord,xCoord))

def IPPplot(iPPtype, cUnits, xyIPP, iNcdName, SubName, spatRef):
    if iPPtype == 'ICP':
        ipPoint = 'AssetsPts'
        iType = 'AssetType'
        iPPtype = 1
        iLat = 'LATITUDE'
        iLong = 'LONGITUDE'
    else:
        ipPoint='Planning_Points'
        iType = 'IPPType'
        iLat = 'Latitude'
        iLong = 'Longitude'
    CoordUnits = cUnits.upper()
    geoUnits=['DECIMAL DEGREES','DEGREES MINUTES SECONDS','DEGREES DECIMAL MINUTES']
    projUnits = ['MGRS', 'US NATIONAL GRID', 'UTM']
    
    spatialRef_Out=spatRef #target output spatial reference
    arcpy.AddMessage(spatialRef_Out.name)
    
    SR_geo = arcpy.SpatialReference('WGS 1984')

    if CoordUnits in geoUnits:
        xy = geoCoords(xyIPP)
        spatialRef_In = SR_geo
        if CoordUnits == 'DECIMAL DEGREES':
            inFormat = 'DD_1'
        elif CoordUnits == 'DEGREES MINUTES SECONDS':
            inFormat = 'DMS_1'
        elif CoordUnits == 'DEGREES DECIMAL MINUTES':
            inFormat = 'DDM_1'
    elif CoordUnits in projUnits:
        xy=xyIPP
        spatialRef_In = spatRef
        if CoordUnits == 'MGRS':
            inFormat = 'MGRS'
        elif CoordUnits == 'US NATIONAL GRID':
            inFormat = 'USNG'
        elif CoordUnits == 'UTM':
            inFormat = 'UTM_ZONES'
    else:
        arcpy.AddErrorMessage('Improper Coordinate System')
        sys.exit('Improper Coordinate System')


    xyTemp='xyTemplate'
    TempTbl = path.join(wrkspc, xyTemp)
    if not arcpy.Exists(TempTbl):
        arcpy.AddMessage("Missing Table: {}".format(xyTemp))
        arcpy.CreateTable_management(wrkspc, xyTemp)
        #Add fields
        fldName = ["x_Field","y_Field","in_Coord","out_Coord"]
        for fld in fldName:
            arcpy.AddField_management(xyTemp,fld,"TEXT",field_length=100)
#    try:
    outFlds=['x_Field', 'in_Coord','out_Coord']
    outInfo=[xy, spatialRef_In.name, spatialRef_Out.name]
    cursor = arcpy.da.InsertCursor(TempTbl, outFlds)
    cursor.insertRow(outInfo)
    del cursor
#    except:
#        arcpy.AddMessage("Could not add IPP/ICP.  Please add manually")
#        sys.exit(0)


    # set parameter values
    outFC = path.join(wrkspc, 'TempPoint')
    x_field = 'x_Field'
    outFormat = 'DD_NUMERIC'
    
    arcpy.ConvertCoordinateNotation_management(TempTbl, outFC, x_field, "", inFormat, \
                                           outFormat, "", spatialRef_Out, spatialRef_In)
    try:
        arcpy.DeleteRows_management(TempTbl)
    except:
        pass

    expression="""{} = '{}'""".format(arcpy.AddFieldDelimiters(outFC, x_field),xy)
    cursor = arcpy.da.SearchCursor(outFC, [x_field, "DDLat", "DDLon"], where_clause=expression)
    pt = arcpy.Point()
    try:
        for row in cursor:
            pt.X=row[2]
            pt.Y=row[1]
            arcpy.AddMessage("Lat: {}, Long: {}".format(pt.Y, pt.X))
    except:
        pass
    del cursor

    if arcpy.Exists(outFC):
        arcpy.Delete_management(outFC)
    ptGeo=arcpy.PointGeometry(pt, SR_geo)
    fc = path.join(wrkspc,ipPoint)

    if ipPoint =="Planning_Points":
        cursor = arcpy.da.InsertCursor(fc,[iType,"SubjNum", iLat, iLong, "SHAPE@"])
        cursor.insertRow([iPPtype,1, pt.Y, pt.X, ptGeo])
    else:
        cursor = arcpy.da.InsertCursor(fc,[iType,"Status", iLat, iLong, "SHAPE@"])
        arcpy.Delete_management(outFC)
        cursor.insertRow([iPPtype,"Assigned",  pt.Y, pt.X, ptGeo])
    try:
        del cursor
    except:
        pass

    return


########
# Main Program starts here
#######
if __name__ == '__main__':
    # Set date and time vars
    timestamp = ''
    now = datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%I_%M_%p")
    OpTime = now.strftime("%d/%m/%y %I:%M %p")
    timestamp = '{0} {1}'.format(todaydate,todaytime)
    
    aprx, df = getMap()

    IncidName = arcpy.GetParameterAsText(0)
    if IncidName == '#' or not IncidName:
        arcpy.AddMessage("No Incident Name provided. It can be entered at a later time.\n")

    IncidNum = arcpy.GetParameterAsText(1)
    if IncidNum == '#' or not IncidNum:
        arcpy.AddMessage("No Incident Number provided. It can be entered at a later time.\n")

    # Get initial operational information: Subject Name, Incidnet Name, Incident
    # Number and Lead Agency
    SubName = arcpy.GetParameterAsText(2)
    if SubName == '#' or not SubName:
        arcpy.AddMessage("No Subject information provided.  It can be entered at a later time.\n")

    LeadAgency = arcpy.GetParameterAsText(3)
    if LeadAgency == '#' or not LeadAgency:
        arcpy.AddMessage("No Lead Agency information provided. It can be entered at a later time.\n")

    TAF2Use = arcpy.GetParameterAsText(4)
    if TAF2Use == '#' or not TAF2Use:
        arcpy.AddError("Need to specify the desired ICS204 form to use.\n")

        #Set the spatial reference
    targetSR = arcpy.GetParameter(5)
    if targetSR == '#' or not targetSR:
        arcpy.AddError("You need to provide a valid Coordinate System")

    #Set the transformation
    targetTrans = arcpy.GetParameterAsText(6)
    if targetTrans == '#' or not targetTrans:
        arcpy.AddMessage("No spatial reference transformation provided")

    iPPtype = arcpy.GetParameterAsText(7)
    if iPPtype == '#' or not iPPtype:
        arcpy.AddMessage("No IPP Type selected\n")
    else:
        if "PLS" in iPPtype:
            iPPtype='PLS'
        elif "LKP" in iPPtype:
            iPPtype='LKP'
        elif "ICP" in iPPtype:
            iPPtype='ICP'

    cUnits = arcpy.GetParameterAsText(8)
    if cUnits == '#' or not cUnits:
        arcpy.AddMessage("No IPP Coordinate Units selected\n")

    ippCoord = arcpy.GetParameterAsText(9)
    if ippCoord == '#' or not ippCoord:
        arcpy.AddMessage('No IPP Coordinates provided\n')
#
    global wrkspc 
    wrkspc= env.workspace
    global wrkFldr 
    wrkFldr= path.dirname(wrkspc)

    # Get a list of datasets in the current gdb
    # Change coordinate system
    datasetList = arcpy.ListDatasets()
    for dat in datasetList:
        dSet=path.join(wrkspc,dat)
        spatial_ref = arcpy.Describe(dSet).spatialReference
        if targetSR.name!=spatial_ref.name:
            arcpy.DefineProjection_management(dSet, targetSR)
        else:
            pass
    
    if SubName:
#        edit = arcpy.da.Editor(wrkspc)
#        edit.startEditing(False, True)
#        edit.startOperation()
        SubjectInfo = path.join(wrkspc,"Subject_Info")
#        subGUID='{' + str(uuid.uuid4()).upper() + '}' 
        with arcpy.da.InsertCursor(SubjectInfo,['SubjNum','Name']) as cursor:
            cursor.insertRow((1, SubName))
#        edit.stopOperation()
#        edit.stopEditing(True)
                
        #Set local parameters
        SubjectInfo = path.join(wrkspc,"Subject_Info")
        TbleText = "Subject Information"
        domTable = SubjectInfo
        codeField = "SubID_txt"
        descField = "Name"
        domName = "SubjectID"
        domDesc = ""
        updateOp = "REPLACE"  
        
        # Process: Create a domain from an existing table          
        cSub=arcpy.GetCount_management(domTable)
        if int(cSub.getOutput(0)) > 0:      
            # Update the attribute table with the GlobalID before updating the domain
            with arcpy.da.SearchCursor(domTable, ['GlobalID']) as cursor:
                for row in cursor:
                    RowID = str(row[0])
                del row
            del cursor
            cursor = arcpy.da.UpdateCursor(domTable,[codeField])
            for row in cursor:
                row[0]=RowID
                cursor.updateRow(row)
            del cursor, row
        
        # Process: Create a domain from an existing table    
            msg="Update {} domain".format(TbleText)
            arcpy.AddMessage(msg)
            try:
                arcpy.TableToDomain_management(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp)
                arcpy.SortCodedValueDomain_management(wrkspc, domName, "DESCRIPTION", "ASCENDING")
            except:
                msg="Unable to update {} domain".format(TbleText)
                arcpy.AddWarning(msg)
                pass  
        else:
            msg="No {} to update".format(TbleText)
            arcpy.AddMessage(msg)



    else:
        arcpy.AddMessage("You have not provided a valid Subject Name")

    if LeadAgency:
        LeadInfo =path.join(wrkspc,"Lead_Agency")
        cursor = arcpy.da.InsertCursor(LeadInfo,['Lead_Agency'])
        row_values=[LeadAgency]
        cursor.insertRow(row_values)
        del cursor
        
        xChk = checkDomain(wrkspc, "Lead_Agency" ,LeadAgency)
        if not xChk:
            arcpy.AddMessage("update Lead Agency domain")
            try:
                arcpy.TableToDomain_management(LeadInfo, "Lead_Agency", "Lead_Agency", wrkspc, "Lead_Agency", "Lead_Agency", "REPLACE")
            except:
                arcpy.AddWarning("Problem with Lead Agency Domain")
                pass
        del xChk
        
        try:
            arcpy.SortCodedValueDomain_management(wrkspc, "Lead_Agency", "DESCRIPTION", "ASCENDING")
        except:
            arcpy.AddWarning("Problem with Lead Agency Domain")
            pass
    else:
        arcpy.AddMessage("You have not provided a valid Lead Agency")

# ## Access to the map Spatial Reference has not been implemented yet.  When it is, turn the statements back on
# #    dfSpatial_Ref = df.spatialReference.name
# #    dfSpatial_Type = df.spatialReference.type
# #    arcpy.AddMessage("\nThe Coordinate System for the dataframe is: " + dfSpatial_Type)
# #    dfSpatial_Type = df.spatialReference.type
# #    arcpy.AddMessage("The Datum for the dataframe is: " + dfSpatial_Ref)
# #    if dfSpatial_Type=='Projected':
# #        arcpy.AddMessage("Be sure to turn on USNG Grid in Data Frame Properties.")
# #    arcpy.AddMessage("\n")

    if IncidName:
        df.name = IncidName # Set the name of the main dataframe to the Incident Name
    elif IncidNum:
        df.name = IncidNum
    IncidInfo = path.join(wrkspc,"Incident_Info")
    fieldnames = [f.name for f in arcpy.ListFields(IncidInfo)]
    if "ICS204" in fieldnames:
        pass
    else:
        arcpy.AddField_management(IncidInfo,"ICS204", "TEXT","","",100,"","","", "Form204")
    if arcpy.Exists(IncidInfo):
        IncidID=subGUID='{' + str(uuid.uuid4()).upper() + '}'
        cursor = arcpy.da.InsertCursor(IncidInfo,['IncidName','IncidNum','MapDatum','ICS204','IncidID'])
        if not IncidName:
            IncidName=''
        if not IncidNum:
            IncidNum=''
        if targetSR:
            if 'WGS' and '84' in targetSR.name:
                tSR='WGS84'
            elif 'NAD' and '27' in targetSR.name:
                tSR='NAD27'
            elif 'NAD' and '83' in targetSR.name:
                tSR='NAD83'
        else:
            tSR='Other'
        if not TAF2Use:
            TAF2Use = "Default"
        cursor.insertRow((IncidName, IncidNum, tSR, TAF2Use,IncidID))
        del cursor

#####################################################################
    formList=checkForm(wrkFldr, TAF2Use)
    # Set local parameters
    domName = "Form_204"
    # Process: Add list of aavailable ICS204 forms to Domain
    #use a for loop to cycle through all the domain codes in the List
    for code in formList:
        arcpy.AddCodedValueToDomain_management(wrkspc, domName, code, code)
###############################################
    arcpy.AddMessage("update Incident Information domain")
    try:
        arcpy.TableToDomain_management(IncidInfo, "IncidName", "IncidID", wrkspc, "Incident_Name", "Incident_Name", "REPLACE")
        arcpy.SortCodedValueDomain_management(wrkspc, "Incident_Name", "DESCRIPTION", "ASCENDING")
    except:
        arcpy.AddWarning("Problem with Incident Information Domain")
        pass
    aprx.save()


    ## Update Opertion Period Information
    OpInfo = path.join(wrkspc,"Operational_Period")
    OpPeriod = 1
    cursor = arcpy.da.InsertCursor(OpInfo,['OpPeriod', 'Start_Date'])
    # Update Operational Period Information    
    arcpy.AddMessage("update Operation Period domain")
    cursor.insertRow((OpPeriod, OpTime))
    del cursor
    try:
        arcpy.TableToDomain_management(OpInfo, "OpPeriod", "OpPeriod", wrkspc, "Period", "OpPeriod", "REPLACE")
        arcpy.SortCodedValueDomain_management(wrkspc, "OpPeriod", "DESCRIPTION", "ASCENDING")
    except:
        pass
#
    if iPPtype:
        if cUnits:
            if ippCoord:
                IPPplot(iPPtype, cUnits, ippCoord, IncidName, SubName, targetSR)
            else:
                pass
        else:
            pass
    else:
        pass


    del aprx, df, wrkspc