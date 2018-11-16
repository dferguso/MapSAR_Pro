# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 23:36:45 2018

@author: ferguson
"""
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



# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

def getMap():
    ## Get current aprx and map
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT");df = aprx.listMaps()[0]
        return(aprx,df)
    except SystemExit as err:
        pass

def createRelationships(df, origin_table, destination_table, origin_primary_key, origin_foreign_key):
    out_relationship_class = "{}_{}".format(origin_table.replace("_",""), destination_table.replace("_",""))
    relationship_type = "SIMPLE"
    forward_label = "{}".format(destination_table.replace("_",""))
    backward_label = "{}".format(origin_table.replace("_",""))
    message_direction = "NONE"
    cardinality = "ONE_TO_MANY"
    attributed = "NONE"
    for lyr in df.listLayers():
        if lyr.name == origin_table:
            origin_table = lyr.longName
        if lyr.name == destination_table:
            destination_table = lyr.longName           
    arcpy.CreateRelationshipClass_management (origin_table, destination_table, out_relationship_class, relationship_type, forward_label, backward_label,message_direction, cardinality, attributed, origin_primary_key, origin_foreign_key)

if __name__ == '__main__':
    global wrkspc 
    wrkspc= env.workspace   
    aprx, df = getMap()

    # Script arguments
    
    createRelationships(df, 'Subject_Info', 'Planning_Points', "SubID_Txt", "SubjectID")    