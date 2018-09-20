# ---------------------------------------------------------------------------
# UpdateDomains.py
# Purpose:  This tools is used repeatedly to update information stored in the
#  SAR_Default.gbd domains.  Use this tool whenever new information is entered
#  into the following feature classes:
# Lead Agency</br>
# Incident Information</br>
# Operation Period</br>
# Incident Staff</br>
# Teams</br>
# Subject Information</br>
# Scenario</br>
# Probability_Regions</br>
# Assignments</br>
# Clues_Point<
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
# Updatd to pro: 07/13/2018
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
from arcpy import env
from os import path
try:
    sys
except NameError:
    import sys

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
                
def updtDomain(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText):
    # Count the rows in the table to make sure there is something to update
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
                
        
def updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText):
    # Count the rows in the table to make sure there is something to update
    cSub=arcpy.GetCount_management(domTable)
    if int(cSub.getOutput(0)) > 0:      
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
        
        
###########Main############
if __name__ == '__main__':
    global wrkFldr
    global Workspace
    
    aprx, df = getMap()
    # Script arguments
    
    wrkspc = arcpy.GetParameterAsText(0)
    if wrkspc == '#' or not wrkspc:
        wrkspc = "MapSAR_Pro.gdb" # provide a default value if unspecified

    env.workspace = wrkspc
    wrkFldr= path.dirname(wrkspc)
    
    # Process: Table To Domain (1)
    domTable = path.join(wrkspc,"Lead_Agency")
    TbleText = "Lead Agency"
    codeField = "Lead_Agency"
    descField = "Lead_Agency"
    domName = "Lead_Agency"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)
    

    # Process: Table To Domain (2)
    domTable = path.join(wrkspc,"Incident_Info")
    TbleText = "Incident Information"
    codeField = "IncidID_txt"
    with arcpy.da.SearchCursor(domTable,['IncidName','IncidNum']) as cursor:
        for row in cursor:
            if row[0]:
                descField = 'IncidName'
            elif row[1]:
                descField = 'IncidNum'
            else:
                descField = 'Name'
        del row
    del cursor
    domName = "Incident_Name"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)

    # Process: Table To Domain (3)
    domTable = path.join(wrkspc,"Operational_Period")
    TbleText = "Op Period"
    codeField = "OpPeriod"
    descField = "OpPeriod"
    domName = "Period"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)
    

    # Process: Table To Domain (4)
    domTable = path.join(wrkspc,"Incident_Staff")
    TbleText = "Incident Staff"
    codeField = "Staff_Name"
    descField = "Staff_Name"
    domName = "StaffName"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)
    

    # Process: Table To Domain (5)
    domTable = path.join(wrkspc,"Teams")
    TbleText = "Teams"
    codeField = "Team_Name"
    descField = "Team_Name"
    domName = "Teams"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)


    # Process: Table To Domain (6)   
    domTable = path.join(wrkspc,"Team_Members")
    TbleText = "Team Members"
    codeField = "Name"
    descField = "Namee"
    domName = "TeamMembers"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)


    # Process: Table To Domain (7)
    #Set local parameters
    domTable = path.join(wrkspc,"Subject_Info")
    TbleText = "Subject Information"
    codeField = "SubID_txt"
    descField = "Name"
    domName = "SubjectID"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText) 


    # Process: Table To Domain (8)
    domTable = path.join(wrkspc,"Scenarios")
    TbleText = "Scenarios"
    codeField = "Scenario_Number"
    descField = "Description"
    domName = "Scenario_Number"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)     
    
    
    # Process: Table To Domain (9)
    domTable = path.join(wrkspc,"Probability_Regions")
    TbleText = "Probability Regions"
    codeField = "Region_Name"
    descField = "Region_Name"
    domName = "ProbRegions"
    domDesc = ""
    updateOp = "REPLACE"
    updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)    
    

    # Process: Table To Domain (10)
    domTable = path.join(wrkspc,"Assignments")
    TbleText = "Assignment Numbers"
    codeField = "Assignment_Number"
    descField = "Assignment_Number"
    domName = "Assignment_Number"
    domDesc = ""
    updateOp = "REPLACE"
    try: 
        updtDomain2(domTable, codeField, descField, wrkspc, domName, domDesc, updateOp,TbleText)
    except:
        arcpy.AddMessage("Error in Assignment Numbers update: may be two Assignments with same number or multiple blanks")
