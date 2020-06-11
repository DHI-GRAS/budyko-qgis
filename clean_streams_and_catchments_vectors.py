#Definition of inputs and outputs
#==================================
##Budyko=group
##Clean-up stream and catchment vectors=name
##ParameterVector|streamVector|Stream Vector|1|False
##ParameterVector|catchmentVector|Catchment Vector|2|False

import numpy as np
from processing.tools import dataobjects
from qgis.core import QgsProcessingException

streamLayer = dataobjects.getObjectFromUri(streamVector)
catchmentLayer = dataobjects.getObjectFromUri(catchmentVector)

feedback.setProgressText("Reading data...")
linkno, s = streamLayer.getValues("LINKNO")
if not s:
    raise QgsProcessingException("Stream vector is missing LINKNO field.")
linknoId = streamLayer.fieldNameIndex("LINKNO")
dslinkno, s = streamLayer.getValues("DSLINKNO")
if not s:
    raise QgsProcessingException("Stream vector is missing DSLINKNO field.")
dslinknoId = streamLayer.fieldNameIndex("DSLINKNO")
uslinkno1, s = streamLayer.getValues("USLINKNO1")
if not s:
    raise QgsProcessingException("Stream vector is missing USLINKNO1 field.")
uslinkno1Id = streamLayer.fieldNameIndex("USLINKNO1")
uslinkno2, s = streamLayer.getValues("USLINKNO2")
if not s:
    raise QgsProcessingException("Stream vector is missing USLINKNO2 field.")
uslinkno2Id = streamLayer.fieldNameIndex("USLINKNO2")
dn, s = catchmentLayer.getValues("DN")
if not s:
    raise QgsProcessingException("Catchment vector is missing DN field.")
dnId = catchmentLayer.fieldNameIndex("DN")

allLinks = np.array(zip(linkno, dslinkno, uslinkno1, uslinkno2))
allLinksNew = np.copy(allLinks)
catchments = np.array([-1] + dn)
catchmentsNew = np.copy(catchments)

feedback.setProgressText("Cleaning data...")
for i, value in enumerate(linkno):
    allLinksNew[allLinks == value] = i
    catchmentsNew[catchments == value] = i
print(catchments)

feedback.setProgressText("Saving stream data...")
total = 100.0 / len(linkno) if len(linkno) > 0 else 1
streamLayer.startEditing()
streamLayer.selectAll()
for i, feature in enumerate(streamLayer.selectedFeaturesIterator()):
    progress.setPercentage(int(i * total))
    streamLayer.changeAttributeValues(feature.id(), {linknoId: int(allLinksNew[i, 0]),
                                                     dslinknoId: int(allLinksNew[i, 1]),
                                                     uslinkno1Id: int(allLinksNew[i, 2]),
                                                     uslinkno2Id: int(allLinksNew[i, 3])}, {})
streamLayer.removeSelection()
if not streamLayer.commitChanges():
    feedback.setProgressText(streamLayer.commitErrors())

feedback.setProgressText("Saving catchment data...")
total = 100.0 / len(linkno) if len(linkno) > 0 else 1
catchmentLayer.startEditing()
catchmentLayer.selectAll()
for i, feature in enumerate(catchmentLayer.selectedFeaturesIterator()):
    progress.setPercentage(int(i * total))
    catchmentLayer.changeAttributeValues(feature.id(), {dnId: int(catchmentsNew[i+1])}, {})
catchmentLayer.removeSelection()
catchmentLayer.renameAttribute(dnId, "ID")
if not catchmentLayer.commitChanges():
    feedback.setProgressText(catchmentLayer.commitErrors())