

from ..Utilities.SingletonBase import Singleton
from .MaterialsCreator import MaterialsCreator
from ..Utilities.AssetData import *

import hou

from six import with_metaclass

class KarmaMaterialFactory(with_metaclass(Singleton)):
    def __init_(self):
        pass
    
    def createMaterial(self, assetData, importParams, importOptions):
        gammaCorrected = ["albedo", "diffuse", "specular", "translucency"]
        
        self.redshiftMaterialSettings = {

            ##########################################
            #
            #      Modified section
            #
            ##########################################

            "mapConnections" :{
                "albedo" : {
                    "input" : "base_color",
                    "output" : "out"
                },
                "translucency" : {
                    "input" : "subsurface_color",
                    "output" : "out"
                },
                "diffuse" : {
                    "input" : "base_color",
                    "output" : "out"
                },

                "roughness" : {
                    "input" : "specular_roughness",
                    "output" : "out"
                },

                "specular" : {
                    "input" : "specular_color",
                    "output" : "out"
                },
                "normal" : {
                    "input" : "normal",
                    "output" : "out"
                },
                "bump" : {
                    "input" : "normal",
                    "output" : "out"
                },
                "opacity" : {
                    "input" : "opacity",
                    "output" : "out"
                },
                "displacement" :{
                    "input" : "displacement",
                    "output" : "out"
                },
                "metalness" : {
                    "input" : "metalness",
                    "output" : "out"
                },
                "cavity" : {
                    "input" : "overall_color",
                    "output" : "out"
                }
                #################################################
            }

        }

        
        materialPath = importParams["materialPath"]
        # redshiftMatBuilder = hou.node(materialPath).createNode("redshift_vopnet", importParams["assetName"])
        #USDmaterialContainer =   
        materialContainer = hou.node(materialPath)
        materialContainer.setGenericFlag(hou.nodeFlag.Material, True)
        mtlxOUT = materialContainer.node("suboutput1")
        mtlxStd = materialContainer.createNode("mtlxstandard_surface")
        mtlxOUT.setInput(0, mtlxStd, 0)
        mtlxDisp = materialContainer.createNode("mtlxdisplacement")
        mtlxDisp.parm("scale").set(0.1)
        mtlxOUT.setInput(1, mtlxDisp, 0)
        mtlxProp = materialContainer.createNode("kma_material_properties")
        mtlxOUT.setInput(2, mtlxProp, 0)
        mtlxOUT.parm("name1").set("surface")
        mtlxOUT.parm("name2").set("displacement")
        mtlxOUT.parm("name3").set("properties")


        uvNode = materialContainer.createNode("usdprimvarreader")
        uvNode.parm("signature").set("float2")
        uvNode.parm("varname").set("st")
        uvTransNode = materialContainer.createNode("usdtransform2d")
        uvTransNode.setNamedInput("in", uvNode, "result")
        uvTransPath = "ch(\"" + str(uvTransNode.path()) 
        uvTransNode.parm("scale2").setExpression(uvTransPath + "/scale1\")" )

        #OUT = OUT.setName("table_lamp")
        #print(OUT.path())
        smNode =  str(materialContainer.path()) + "/StandardMaterial1"
        #rsmatOUT = str(hou.node(materialPath).path()) + "/" + "redshift_usd_material1"
        #print(smNode)
        #shaderNode = shaderUSDNode.createNode("redshift::StandardMaterial") ###modified####
        # shaderNode.parm("refl_brdf").set("1")
        # shaderNode.parm("refl_fresnel_mode").set("2")
        #materialNode = materialContainer.createNode("redshift_material", importParams["assetName"])
        #materialNode.setNamedInput("Surface", shaderNode, "outColor")
        shaderNode = mtlxStd
        materialNode = mtlxOUT

        normalPriority = False      
        isAlbedoPath = None
        for textureData in assetData["components"]:

            if textureData["type"]:
                
               
                textureNode = materialContainer.createNode("mtlximage", textureData["type"])
                textureNode.parm("file").set(textureData["path"].replace("\\", "/"))
                textureNode.setNamedInput("texcoord", uvTransNode, "result")
                if textureData["type"] == "albedo":
                    textureNode.parm("filecolorspace").set("srgb_tx")
                    isAlbedoPath = True
                else:
                    textureNode.parm("filecolorspace").set("Raw")
                   


            if textureData["type"] not in self.redshiftMaterialSettings["mapConnections"].keys(): continue
            textureParams =  self.redshiftMaterialSettings["mapConnections"][textureData["type"]]

            if textureData["type"] == "translucency":
                textureNode.parm("filecolorspace").set("srgb_tx")
                textureNode.parm("signature").set("color3")
                shaderNode.parm("subsurface").set(0.5)
                shaderNode.parm("thin_walled").set("1")

            # if textureData["type"] in gammaEnabled:
            #     textureNode.parm("tex0_gammaoverride").set(1)

            if textureData["type"] == "roughness":
                rampNode = materialContainer.createNode("kma_rampconst")
                rampNode.setNamedInput("t", textureNode, "out" )                
                shaderNode.setNamedInput(textureParams["input"], rampNode, textureParams["output"])

            elif textureData["type"] == "opacity":
                textureNode.parm("signature").set("default")
                shaderNode.setNamedInput(textureParams["input"], textureNode, textureParams["output"] )

            elif textureData["type"] == "metalness":
                textureNode.parm("signature").set("default")
                shaderNode.setNamedInput(textureParams["input"], textureNode, textureParams["output"] )

            elif textureData["type"] == "normal":
                normalNode = materialContainer.createNode("mtlxnormalmap")  
                normalNode.parm("scale").set(0.1)           
                shaderNode.setNamedInput(textureParams["input"], normalNode, textureParams["output"])
                normalNode.setNamedInput("in", textureNode, "out")
                textureNode.parm("signature").set("color3")
                normalPriority = True                
                

            elif textureData["type"] == "bump":
                bumpNode = materialContainer.createNode("mtlxbump")                
                if normalPriority == False:
                    shaderNode.setNamedInput(textureParams["input"], bumpNode, textureParams["output"])   
                bumpNode.setNamedInput("height", textureNode, "out")              
            

            elif textureData["type"] == "displacement":
                remapNode = materialContainer.createNode("mtlxremap")
                remapNode.setNamedInput("in", textureNode, "out" )                
                #mtlxDisp.setNamedInput(textureParams["input"], remapNode, textureParams["output"])
                textureNode.parm("signature").set("default")      
                remapNode.parm("outlow").set(-0.5)
                remapNode.parm("outhigh").set(0.5)
                #materialNode.setNamedInput(textureParams["input"], mtlxDisp, textureParams["output"])
                #dispNode.setNamedInput("texMap", textureNode, "outColor")

            elif textureData["type"] == "albedo" or textureData["type"] == "diffuse":
                ccNode = materialContainer.createNode("mtlxcolorcorrect")
                #ccNode.parm("gamma").set(0.5)
                ccNode.setNamedInput("in", textureNode, "out")
                shaderNode.setNamedInput("base_color", ccNode, "out")

              

            else:                
                shaderNode.setNamedInput(textureParams["input"], textureNode, textureParams["output"])


            hou.node(importParams["materialPath"]).layoutChildren()
                


            
           
        
        return materialNode


class KarmaTriplanarFactory(with_metaclass(Singleton)):
    def __init__(self):
        pass

    def createMaterial(self, assetData, importParams, importOptions):
        self.triplanarSettings = {
            ##########################################
            #
            #      Modified section
            #
            ##########################################
            "mapConnections" : {
                "albedo" : "base_color",
                "diffuse" : "base_color",
                "roughness" : "refl_roughness",
                "specular" : "refl_color",
                "normal" : "bump_input",
                "bump" : "BumpMap",
                "opacity" : "opacity_color",
                "displacement" : "Displacement",
                "metalness" : "metalness"
            ############################################    
            }

        }

        materialContainer = hou.node(importParams["materialPath"])        
        shaderNode = materialContainer.createNode("redshift::StandardMaterial") ###modified#####
        # shaderNode.parm("refl_brdf").set("1")
        # shaderNode.parm("refl_fresnel_mode").set("2")
        materialNode = materialContainer.createNode("redshift_material", importParams["assetName"])
        materialNode.setNamedInput("Surface", shaderNode, "outColor")
        triplanarNode = materialContainer.createNode("quixel_redshift_triplanar::1.0")
        for textureData in assetData["components"]:            
            if triplanarNode.parm(textureData["type"]) is not None:
                triplanarNode.parm(textureData["type"]).set(textureData["path"].replace("\\", "/"))
                if textureData["type"] not in self.triplanarSettings["mapConnections"].keys(): continue

                if textureData["type"] == "displacement":
                    dispNode = materialContainer.createNode("redshift::Displacement")
                    materialNode.setNamedInput("Displacement", dispNode, "out")
                    dispNode.setNamedInput("texMap", triplanarNode, "displacement")

                elif textureData["type"] == "bump" :
                    bumpNode = materialContainer.createNode("redshift::BumpMap")
                    materialNode.setNamedInput("Bump Map", bumpNode, "out")   
                    bumpNode.setNamedInput("input", triplanarNode, "bump")
                else:
                    shaderNode.setNamedInput(self.triplanarSettings["mapConnections"][textureData["type"]], triplanarNode, textureData["type"])

        return materialNode

       



def registerMaterials():
    
    # materialTypes = ["Principled", "Triplanar"]
    karma = KarmaMaterialFactory()
    karmaTriplanar = KarmaTriplanarFactory()
    materialsCreator = MaterialsCreator()
    materialsCreator.registerMaterial("Karma", "Karma", karma.createMaterial)
    

registerMaterials()
