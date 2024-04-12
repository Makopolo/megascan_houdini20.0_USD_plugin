import hou
from .SingletonBase import Singleton
from ..MaterialsSetup.MaterialsCreator import MaterialsCreator

from six import with_metaclass

##########################################
#
#      Modified section
#
##########################################
from ..AssetImporters.ImportSurface import ImportSurface 

def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s
##############################################

class AtlasSplitter(with_metaclass(Singleton)):
    def __init__(self):
        pass

    def splitAtlas(self, assetData, importOptions, importParams, materialPath):
        
        atlasMeshOutputs = []
        geometryContainer = hou.node(importParams["assetPath"]).createNode("geo", "Atlas_Splitter")
        if importOptions["UI"]["ImportOptions"]["Renderer"] == "Redshift":
            geometryContainer.parm("RS_objprop_displace_enable")#.set(1)
            geometryContainer.parm("RS_objprop_displace_scale")#.set(0.01)

        elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Arnold":
            geometryContainer.parm("ar_disp_height").set(0.008)
        splitterNode = geometryContainer.createNode("quixel_atlas_splitter::1.0")
        opacityMapPath = [opacityMap["path"] for opacityMap in assetData["components"] if opacityMap["type"] == "opacity"]
        splitterNode.parm("filename").set(opacityMapPath[0])
        ##########################################
        #
        #      Modified section
        #
        ##########################################
        normalVert = splitterNode.createOutputNode("normal")

        ##############################################
        
        materialNode = normalVert.createOutputNode("material")
        materialNode.parm("shop_materialpath1").set(materialPath)
        outputNull = materialNode.createOutputNode("null", importParams["assetName"])

        atlasGeometry = outputNull.geometry()
        primitveAttribs = atlasGeometry.primAttribs()
        nameAttrib = [attrib for attrib in primitveAttribs if attrib.name()=="name"][0]
        scatterGroups = nameAttrib.strings()
        for scatterGroup in scatterGroups:
            blastGroup = outputNull.createOutputNode("blast")
            blastGroup.parm("group").set("@name=" + scatterGroup)
            blastGroup.parm("negate").set(1)
            atlasPiece = blastGroup.createOutputNode("null", scatterGroup)
            atlasPiece.setDisplayFlag(True)
            atlasPiece.setRenderFlag(True)
            atlasMeshOutputs.append(atlasPiece)
        geometryContainer.moveToGoodPosition()
        hou.node(importParams["assetPath"]).moveToGoodPosition()

        ##########################################
        #
        #      Modified section
        #
        ##########################################
        if importOptions["UI"]["ImportOptions"]["EnableUSD"]:
            assName = rchop(importParams["assetName"],"_0")
            container = hou.node("/stage").createNode("subnet",importParams["assetName"])
            path = "/stage/" + importParams["assetName"]
            objPath = "/obj/" + importParams["assetName"] + "/Atlas_Splitter/"

            compVari = hou.node(path).createNode('componentgeometryvariants')
            #compVari.setNextInput()
            if importOptions["UI"]["USDOptions"]["USDMaterial"] == "Karma":
                importOptions["UI"]["ImportOptions"]["Renderer"] = "Karma"
                importOptions["UI"]["ImportOptions"]["Material"] = "Karma"
                importOptions["UI"]["ImportOptions"]["USDmatLoop"] = True
            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Redshift_USD":
                importOptions["UI"]["ImportOptions"]["Renderer"] = "Redshift"
                importOptions["UI"]["ImportOptions"]["Material"] = "Redshift"

            for scatterGroup in scatterGroups:
                compGeoNode = hou.node(path).createNode('componentgeometry', assName + "_0")
                compGeoNode.parm("sourceinput").set(2)
                compGeoNode.parm("sourcesop").set(objPath + scatterGroup)
                compVari.setNextInput(compGeoNode)
                
            
            matCont = hou.node(path).createNode("materiallibrary", importParams["assetName"])
            importParams["materialPath"] = matCont.path()
            importParams["importType"] = "USD"    
            
            #print(importOptions)

            # if importOptions["UI"]["ImportOptions"]["Renderer"] == "Karma":
            #     importOptions["UI"]["ImportOptions"]["Renderer"] = "Karma"
            #     importOptions["UI"]["ImportOptions"]["Material"] = "Karma"
            #     importOptions["UI"]["ImportOptions"]["USDmatLoop"] = True
            #Starts the ImportSurface.py to see which renderer is used make the materialinside the material library 
            ImportSurface().importAsset(assetData, importOptions, importParams)
            
            matCont.parm("matpathprefix").set("/ASSET/mtl/")
            matCont.parm("matnode1").set("*")

            #Create component material node set material path and connect the node to component varient and material
            compMaterial = hou.node(path).createNode('componentmaterial')
            #compMaterial.parm("matspecpath1").set("/ASSET/mtl/"+ importParams["assetName"])
            compMaterial.setNextInput(compVari)
            compMaterial.setNextInput(matCont)

            #Create Compoenet geometry output node and set varient mode on
            compOutput = hou.node(path).createNode('componentoutput',importParams["assetName"]+"_ASSET")
            compOutput.parm("variantlayers").set(1)
            compOutput.parm("setdefaultvariants").set(1)
            compOutput.setNextInput(compMaterial)
            compOutput.setDisplayFlag(True)
            subnetOutputNode = hou.node(path).node("output0")
            subnetOutputNode.setInput(0, compOutput)
            hou.node(path).layoutChildren()

                

#################################################################
        return atlasMeshOutputs

