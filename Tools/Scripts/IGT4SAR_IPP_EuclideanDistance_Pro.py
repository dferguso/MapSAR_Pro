# ---------------------------------------------------------------------------
# Name:        IPP_EuclideanDistance2.py
#
# Purpose:   Creates the Statistical Search Area around the IPP using Ring Model
#  (25%, 50%, 75% and 95%) based on historical data related to Lost Person
#  Behavior.  Specific subject category is obtained from the Subject
#  Information.  IPP Distances are provided by Robert Koester (dbs Productions -
#  Lost Person Behvaior) and are not included in this copyright.
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
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
# Import arcpy module
try:
    arcpy
except NameError:
    import arcpy

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

def getMap():
    ## Get current aprx and map
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT");df = aprx.listMaps()[0]
        return(aprx,df)

    except SystemExit as err:
        pass

def RingDistances(Subject_Category, EcoReg, Terrain):
    #'Subject_Category':{'Temperate':{'Mountainous':,'Flat':},'Dry':{'Mountainous':,'Flat':},'Urban':{'Mountainous':,'Flat':}}
    lpb={'Abduction':[0.2,1.5,12.0],
         'Aircraft':[0.4,0.9,3.7,10.4],
         'Angler':{'Temperate':{'Mountainous':[0.2,0.9,3.4,6.1],'Flat':[0.5,1.0,3.4,6.1]},'Dry':[2.0,6.0,6.5,8.0]},
         'All Terrain Vehicle':[1.0,2.0,3.5,5.0],
         'Autistic':{'Temperate':[0.4,1.0,2.3,9.5],'Urban':[0.2,0.6,2.4,5.0]},
         'Camper':{'Temperate':{'Mountainous':[0.1,1.4,1.9,24.7],'Flat':[0.1,0.7,2.0,8.0]},'Dry':{'Mountainous':[0.4,1.0,2.6,20.3]}},
         'Child (1-3)':{'Temperate':{'Mountainous':[0.1,0.2,0.6,2.0],'Flat':[0.1,0.2,0.6,2.0]},'Dry':[0.4,1.2,2.0,5.1],'Urban':[0.1,0.3,0.5,0.7]},
         'Child (4-6)':{'Temperate':{'Mountainous':[0.1,0.5,0.9,2.3],'Flat':[0.1,0.4,0.9,4.1]},'Dry':[0.4,1.2,2.0,5.1],'Urban':[0.06,0.3,0.6,2.1]},
         'Child (7-9)':{'Temperate':{'Mountainous':[0.5,1.0,2.0,7.0],'Flat':[0.1,0.5,1.3,5.0]},'Dry':[0.3,0.8,2.0,4.5],'Urban':[0.1,0.3,0.9,3.2]},
         'Child (10-12)':{'Temperate':{'Mountainous':[0.5,1.0,2.0,5.6],'Flat':[0.3,1.0,3.0,6.2]},'Dry':[0.5,1.3,4.5,10.0],'Urban':[0.2,0.9,1.8,3.6]},
         'Child (13-15)':{'Temperate':{'Mountainous':[0.5,1.3,3.0,13.3],'Flat':[0.4,0.8,2.0,6.2]},'Dry':[1.5,2.0,3.0,7.4]},
         'Climber':[0.1,1.0,2.0,9.2],
         'Dementia':{'Temperate':{'Mountainous':[0.2,0.7,2.0,13.3],'Flat':[0.2,0.6,1.5,7.9]},'Dry':{'Mountainous':[0.6,1.2,1.9,3.8],'Flat':[0.3,1.0,2.2,7.3]},'Urban':[0.2,0.7,2.0,7.8]},
         'Despondent':{'Temperate':{'Mountainous':[0.2,0.7,2.0,13.3],'Flat':[0.2,0.5,1.4,10.7]},'Dry':{'Mountainous':[0.5,1.0,2.1,11.1],'Flat':[0.3,1.2,2.3,12.8]},'Urban':[0.06,0.3,0.9,8.1]},
         'Gatherer':{'Temperate':[0.9,2.0,4.0,8.0],'Dry':[1.0,1.6,3.6,6.9],'Urban':[0.9,2.0,4.0,8.0]},
         'Hiker':{'Temperate':{'Mountainous':[0.7,1.9,3.6,11.3],'Flat':[0.4,1.1,2.0,6.1]},'Dry':{'Mountainous':[1.0,2.0,4.0,11.9],'Flat':[0.8,1.3,4.1,8.1]}},
         'Horseback Rider':[0.2,2.0,5.0,12.2],
         'Hunter':{'Temperate':{'Mountainous':[0.6,1.3,3.0,10.7],'Flat':[0.4,1.0,1.9,8.5]},'Dry':{'Mountainous':[1.3,3.0,5.0,13.8],'Flat':[1.0,1.9,4.0,7.0]}},
         'Mental Illness':{'Temperate':{'Mountainous':[0.4,1.4,5.1,9.0],'Flat':[0.5,0.6,1.4,5.0]},'Urban':[0.2,0.4,0.9,7.7]},
         'Mental Retardation':{'Temperate':{'Mountainous':[0.4,1.0,2.0,7.0],'Flat':[0.2,0.6,1.3,7.3]},'Dry':[0.7,2.5,5.4,38.9],'Urban':[0.2,0.5,2.3,6.14]},
         'Mountain Biker':{'Temperate':[1.9,2.5,7.0,15.5],'Dry':[1.7,4.0,8.2,18.1]},
         'Other (Extreme Sport)':[0.3,1.6,3.5,8.3],
         'Runner':[0.9,1.6,2.1,3.6],
         'Skier-Alpine':[0.7,1.7,3.0,9.4],
         'Skier-Nordic':{'Temperate':[1.0,2.2,4.0,12.2],'Dry':[1.2,2.7,4.0,12.1]},
         'Snowboarder':[1.0,2.0,3.8,9.5],
         'Snowmobiler':{'Temperate':{'Mountainous':[2.0,4.0,6.9,10.0],'Flat':[0.8,2.9,25.5,59.7]},'Dry':[1.0,3.0,8.7,18.9]},
         'Substance Abuse':[0.3,0.7,2.6,6.0],
         'Default':[0.4,1.1,2.0,6.1]
        }
    
    if Subject_Category not in lpb:
        arcpy.AddMessage('Specified Subject Category not available\n')
        arcpy.AddMessage('Choose from the following:')
        for ky in list(lpb.keys()):
            arcpy.AddMessage(ky)
        return()
    else:
        Distances=lpb[Subject_Category]
        if isinstance(Distances, dict):
            if EcoReg not in Distances:
                arcpy.AddMessage('Specified EcoRegion not available\n')
                arcpy.AddMessage('Choose from the following:')
                for ky in list(Distances.keys()):
                    arcpy.AddMessage(ky)
                return

            else:
                Distances=Distances[EcoReg]
                if isinstance(Distances, dict):
                    if Terrain not in Distances:
                        arcpy.AddMessage('Specified Terrain not available\n')
                        arcpy.AddMessage('Choose from the following:')
                        for ky in list(Distances.keys()):
                            arcpy.AddMessage(ky)
                        return
                    else:
                        Distances=Distances[Terrain]
                return(Distances)
        else:
            if EcoReg:
                arcpy.AddMessage('Specific EcoRegion data for "{}" is not available.  Only general ' \
                'distances available for this Subject Category\n'.format(EcoReg))
            if Terrain:
                arcpy.AddMessage('Specific Terrain data for "{}" is not available. Only general ' \
                'distances available for this Subject Category\n'.format(Terrain))
        return(Distances)

if __name__ == '__main__':

    aprx, df = getMap()

    # Script arguments
    SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
    IPP = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP
    UserSelect = arcpy.GetParameterAsText(2)  # Subejct Category or User Defined Values
    bufferUnit = arcpy.GetParameterAsText(3) # Desired units
    IPPDists = arcpy.GetParameterAsText(4)  # Optional - User entered distancesDetermine to use PLS or LKP

    SubNum = int(SubNum)
    fc1="Incident_Info"

    EcoReg = "Temperate"
    Terrain = "Mountainous"
    PopDen = "Wilderness"

    try:
        rows = arcpy.SearchCursor(fc1)
        row = rows.next()

        while row:
            # you need to insert correct field names in your getvalue function
            EcoReg = row.getValue("Eco_Region")
            Terrain = row.getValue("Terrain")
            PopDen = row.getValue("Pop_Den")
            row = rows.next()
        del rows
        del row

    except:
        EcoReg = "Temperate"
        Terrain = "Mountainous"
        PopDen = "Wilderness"
        arcpy.AddWarning("No Incident Information provided. Default values used.")
        arcpy.AddWarning("Eco_Region = Temperate; Terrain = Mountainous; Population Density = Wilderness.")
        arcpy.AddWarning("If inappropriate...Remove Statistical Search Area Layer, \nprovide Incident Information and re-run\n")

    fc2 = "Subject_Info"
    where = '"Subject_Number"= {}'.format(SubNum)
    rows = arcpy.SearchCursor(fc2, where)
    row = rows.next()

    while row:
        # you need to insert correct field names in your getvalue function
        Subject_Category = row.getValue("Category")
        row = rows.next()
    del rows
    del row
    del where

    if UserSelect=='User Defined Values':
        arcpy.AddMessage(IPPDists)
        Dist = IPPDists.split(',')
        Distances=[float(i) for i in Dist]
        Distances.sort()
        mult = 1.0
    else:
        if bufferUnit =='kilometers':
            mult = 1.6093472
        else:
            mult = 1.0
    #    bufferUnit = "miles"
        Distances = RingDistances(Subject_Category, EcoReg, Terrain)
    
    #Add a ROW onto the distances
    Distances.append(round(Distances[-1]*1.5,2))
    arcpy.AddMessage(Distances)

    # Identify the IPP Feature Layer
    for lyr in df.listLayers():
        if lyr.isFeatureLayer:
            arcpy.SelectLayerByAttribute_management(lyr.longName, 'CLEAR_SELECTION')
        if lyr.name == "Planning Points":
            fc3 = lyr

    where1 = '"Subject_Number" = {}'.format(str(SubNum))
    where2 = ' AND "IPPType" = ' + ("'{}'".format(IPP))
    where = where1 + where2
    
    arcpy.SelectLayerByAttribute_management(fc3, "NEW_SELECTION", where)
    arcpy.AddMessage("Buffer IPP around the {}".format(IPP))
	
    dissolve_option = "ALL"

    k=0

    rows = arcpy.SearchCursor(fc3, where)
    for row in rows:
    ##row = rows.next()
        k=1
        if bufferUnit =='kilometers':
            fieldName3 = "Area_SqKm"
            fieldAlias3 = "Area (sq km)"
            expression3 = "round(!shape.area@squarekilometers!,2)"
            pDistIPP = '"IPPDist"'

        else:
            fieldName3 = "Area_SqMi"
            fieldAlias3 = "Area (sq miles)"
            expression3 = "round(!shape.area@squaremiles!,2)"
            pDistIPP = '"IPPDist"'

        perct = ['25%', '50%', '75%', '95%', 'ROW']
        inFeatures = "Planning\StatisticalArea"
        fieldName1 = "Descrip"
        fieldName2 = "Area_Ac"
        fieldName4 = "Sub_Cat"

        fieldAlias1 = "Description"
        fieldAlias2 = "Area (Acres)"
        fieldAlias4 = "Subject Category"

        expression2 = "int(!shape.area@acres!)"

        pDist=[]
        for x in Distances:
            pDist.append(round(x * mult,2))

        arcpy.AddMessage("Units = {}".format(bufferUnit))
        arcpy.AddMessage(pDist)

        while row:
            # you need to insert correct field names in your getvalue function
            arcpy.MultipleRingBuffer_analysis(fc3, inFeatures, pDist, bufferUnit, "DistFrmIPP")#, dissolve_option, "FULL")
            row = rows.next()

        del rows
        del row
        del where

        arcpy.AddMessage('Completed multi-ring buffer')

        arcpy.AddField_management(inFeatures, fieldName1, "TEXT", "", "", "25",
                                  fieldAlias1, "NULLABLE", "","PrtRange")
        arcpy.AddField_management(inFeatures, fieldName2, "DOUBLE", "", "", "",
                                  fieldAlias2, "NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName3, "DOUBLE", "", "", "",
                                  fieldAlias3, "NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName4, "TEXT", "", "", "25",
                                  fieldAlias4, "NULLABLE", "","PrtRange")

        arcpy.AddMessage('Completed AddFields')

        arcpy.CalculateField_management(inFeatures, fieldName2, expression2,
                                            "PYTHON")
        arcpy.CalculateField_management(inFeatures, fieldName3, expression3,
                                            "PYTHON")

        rows = arcpy.UpdateCursor(inFeatures)
        arcpy.AddMessage('Completed update cursor')
        row = rows.next()

        k=0
        while row:
            # you need to insert correct field names in your getvalue function
            row.setValue(fieldName1, perct[k])
            row.setValue(fieldName4, Subject_Category)
            arcpy.AddMessage('Completed setValues')
            rows.updateRow(row)
            k=k+1
            row = rows.next()

        del rows
        del row

        # create a new layer
        if arcpy.Exists(inFeatures):
            arcpy.AddMessage('Insert inFeatures')
            newLyr = 'StatArea'
            grpLyr = 'Statistical Search Area'
            results = arcpy.MakeFeatureLayer_management(inFeatures,newLyr).getOutput(0) 
            if df.listLayers(grpLyr)[0].isGroupLayer:
                refGroupLayer = df.listLayers(grpLyr)[0]
                df.addLayerToGroup(refGroupLayer, results, 'TOP')
                lyr=df.listLayers(newLyr)[0]
#                try:
                # Set layer that output symbology will be based on
                symbologyLayer = r"C:\MapSAR_Pro\Tools\Layers\StatisticalSearchArea.lyrx"
                if arcpy.Exists(symbologyLayer):
                    symLyrFile = arcpy.mp.LayerFile(symbologyLayer)
                    df.addLayer(symLyrFile,"TOP")
                    symLyr = df.listLayers()[0]
                    symObj=symLyr.symbology
                    df.removeLayer(symLyr)
                    lyr.symbology=symObj
                    aprx.save()
                    # Apply the symbology from the symbology layer to the input layer
                    # arcpy.ApplySymbologyFromLayer_management(results, symbologyLayer,[['VALUE_FIELD', 'Descrip', 'Descrip']])
                    arcpy.AddMessage("Add default symbology")
#                except:
#                    arcpy.AddMessage("No Symbology added")
#                    pass
#        
            else:
                arcpy.AddMessage("Where is Waldo")

    if k == 0:
        arcpy.AddMessage("There was no {} defined".format(IPP))



