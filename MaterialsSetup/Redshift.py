

from ..Utilities.SingletonBase import Singleton
from .MaterialsCreator import MaterialsCreator
from ..Utilities.AssetData import *

import hou

from six import with_metaclass

class RedshiftMaterialFactory(with_metaclass(Singleton)):
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
                    "output" : "outColor"
                },
                "translucency" : {
                    "input" : "ms_color",
                    "output" : "outColor"
                },
                "diffuse" : {
                    "input" : "base_color",
                    "output" : "outColor"
                },

                "roughness" : {
                    "input" : "refl_roughness",
                    "output" : "outColor"
                },

                "specular" : {
                    "input" : "refl_color",
                    "output" : "outColor"
                },
                "normal" : {
                    "input" : "bump_input",
                    "output" : "out"
                },
                "bump" : {
                    "input" : "bump_input",
                    "output" : "out"
                },
                "opacity" : {
                    "input" : "opacity_color",
                    "output" : "outColor"
                },
                "displacement" :{
                    "input" : "Displacement",
                    "output" : "out"
                },
                "metalness" : {
                    "input" : "metalness",
                    "output" : "outR"
                },
                "cavity" : {
                    "input" : "overall_color",
                    "output" : "outColor"
                }
                #################################################
            }

        }
        materialPath = importParams["materialPath"]
        materialContainer = hou.node(materialPath)        
        shaderNode = materialContainer.createNode("redshift::StandardMaterial") ###modified####
        materialNode = materialContainer.createNode("redshift_material", importParams["assetName"])
        materialNode.setNamedInput("Surface", shaderNode, "outColor")

        normalPriority = False      
        isAlbedoPath = None
        for textureData in assetData["components"]:

            if textureData["type"] != "opacity":
                textureNode = materialContainer.createNode("redshift::TextureSampler", textureData["type"])
                textureNode.parm("tex0").set(textureData["path"].replace("\\", "/"))
                if textureData["type"] == "albedo":
                    textureNode.parm("tex0_colorSpace").set("sRGB")
                    albedoOffPath = "ch(\"" + str(textureNode.path()) 
                    
                    textureNode.parm("scale2").setExpression(albedoOffPath + "/scale1\")" )
                    
                    isAlbedoPath = True
                else:
                    textureNode.parm("tex0_colorSpace").set("Raw")
                    if isAlbedoPath == True:
                        textureNode.parm("scale1").setExpression(albedoOffPath + "/scale1\")" )
                        textureNode.parm("scale2").setExpression(albedoOffPath + "/scale2\")" )
                        textureNode.parm("offset1").setExpression(albedoOffPath + "/offset1\")" )
                        textureNode.parm("offset2").setExpression(albedoOffPath + "/offset2\")" )
                        textureNode.parm("rotate").setExpression(albedoOffPath + "/rotate\")" )

            if textureData["type"] not in self.redshiftMaterialSettings["mapConnections"].keys(): continue
            textureParams =  self.redshiftMaterialSettings["mapConnections"][textureData["type"]]

            if textureData["type"] == "translucency":
                textureNode.parm("tex0_colorSpace").set("sRGB")
                shaderNode.parm("ms_amount").set(0.5)
                shaderNode.parm("refr_thin_walled").set("1")

            if textureData["type"] == "roughness":
                rampNode = materialContainer.createNode("redshift::RSRamp")
                rampNode.setNamedInput("input", textureNode, "outColor" )                
                shaderNode.setNamedInput(textureParams["input"], rampNode, textureParams["output"])

            elif textureData["type"] == "opacity":
                spriteNode = materialContainer.createNode("redshift::Sprite")
                spriteNode.setNamedInput("input", shaderNode, "outColor")
                materialNode.setNamedInput("Surface", spriteNode, "outColor")
                spriteNode.parm("tex0").set(textureData["path"].replace("\\", "/"))
                spriteNode.parm("tex0_colorSpace").set("Raw")

            elif textureData["type"] == "metalness":
                channelSplitter2 = materialContainer.createNode("redshift::RSColorSplitter")
                shaderNode.setNamedInput(textureParams["input"], channelSplitter2, textureParams["output"])
                channelSplitter2.setNamedInput("input", textureNode, "outColor" )

            elif textureData["type"] == "normal":
                normalNode = materialContainer.createNode("redshift::BumpMap")
                normalNode.parm("inputType").set("1")                

                shaderNode.setNamedInput(textureParams["input"], normalNode, textureParams["output"])
                normalNode.setNamedInput("input", textureNode, "outColor")
                normalPriority = True                
                

            elif textureData["type"] == "bump":
                bumpNode = materialContainer.createNode("redshift::BumpMap")                
                if normalPriority == False:
                    shaderNode.setNamedInput(textureParams["input"], bumpNode, textureParams["output"])   
                bumpNode.setNamedInput("input", textureNode, "outColor")              
            

            elif textureData["type"] == "displacement":
                exrPath = getExrDisplacement(textureData["path"])                
                textureNode.parm("tex0").set(exrPath.replace("\\", "/"))
                dispNode = materialContainer.createNode("redshift::Displacement")
                dispNode.parm("newrange_min").set(-0.5)
                dispNode.parm("newrange_max").set(0.5)


                materialNode.setNamedInput(textureParams["input"], dispNode, textureParams["output"])
                dispNode.setNamedInput("texMap", textureNode, "outColor")

            elif textureData["type"] == "albedo" or textureData["type"] == "diffuse":
                ccNode = materialContainer.createNode("redshift::RSColorCorrection")
                ccNode.setNamedInput("input", textureNode, "outColor")
                shaderNode.setNamedInput("base_color", ccNode, "outColor")

              

            else:                
                shaderNode.setNamedInput(textureParams["input"], textureNode, textureParams["output"])


            hou.node(importParams["materialPath"]).layoutChildren()
                


            
           
        
        return materialNode


class RedshiftTriplanarFactory(with_metaclass(Singleton)):
    def __init__(self):
        pass

    def createMaterial(self, assetData, importParams, importOptions):
        self.triplanarSettings = {

            ##########################################
            #
            #      Modified section
            #
            ##########################################

            "mapConnections" :{
                "albedo" : {
                    "input" : "base_color",
                    "output" : "outColor"
                },
                "translucency" : {
                    "input" : "ms_color",
                    "output" : "outColor"
                },
                "diffuse" : {
                    "input" : "base_color",
                    "output" : "outColor"
                },

                "roughness" : {
                    "input" : "refl_roughness",
                    "output" : "outColor"
                },

                "specular" : {
                    "input" : "refl_color",
                    "output" : "outColor"
                },
                "normal" : {
                    "input" : "bump_input",
                    "output" : "out"
                },
                "bump" : {
                    "input" : "bump_input",
                    "output" : "out"
                },
                "opacity" : {
                    "input" : "opacity_color",
                    "output" : "outColor"
                },
                "displacement" :{
                    "input" : "Displacement",
                    "output" : "out"
                },
                "metalness" : {
                    "input" : "metalness",
                    "output" : "outR"
                },
                "cavity" : {
                    "input" : "overall_color",
                    "output" : "outColor"
                }
                #################################################
            }

        }
        materialPath = importParams["materialPath"]
        # redshiftMatBuilder = hou.node(materialPath).createNode("redshift_vopnet", importParams["assetName"])
        materialContainer = hou.node(materialPath)        
        shaderNode = materialContainer.createNode("redshift::StandardMaterial") ###modified####
        # shaderNode.parm("refl_brdf").set("1")
        # shaderNode.parm("refl_fresnel_mode").set("2")
        materialNode = materialContainer.createNode("redshift_material", importParams["assetName"])
        materialNode.setNamedInput("Surface", shaderNode, "outColor")
        isAlbedoPath = None
        normalPriority = False      
 
        for textureData in assetData["components"]:

            if textureData["type"] != "opacity":
                textureNode = materialContainer.createNode("redshift::TextureSampler", textureData["type"])
                textureNode.parm("tex0").set(textureData["path"].replace("\\", "/"))
                if textureData["type"] == "albedo":
                    textureNode.parm("tex0_colorSpace").set("sRGB")
                    albedoOffPath = "ch(\"" + str(textureNode.path()) 
                    
                    textureNode.parm("scale2").setExpression(albedoOffPath + "/scale1\")" )
                    
                    isAlbedoPath = True
                else:
                    textureNode.parm("tex0_colorSpace").set("Raw")
                    if isAlbedoPath == True:
                        textureNode.parm("scale1").setExpression(albedoOffPath + "/scale1\")" )
                        textureNode.parm("scale2").setExpression(albedoOffPath + "/scale2\")" )
                        textureNode.parm("offset1").setExpression(albedoOffPath + "/offset1\")" )
                        textureNode.parm("offset2").setExpression(albedoOffPath + "/offset2\")" )
                        textureNode.parm("rotate").setExpression(albedoOffPath + "/rotate\")" )

            if textureData["type"] not in self.triplanarSettings["mapConnections"].keys(): continue
            textureParams =  self.triplanarSettings["mapConnections"][textureData["type"]]


            triNode = materialContainer.createNode("redshift::TriPlanar")
            triNode.setNamedInput("imageX", textureNode, "outColor")


            if textureData["type"] == "translucency":
                shaderNode.parm("ms_amount").set(0.5)
                shaderNode.parm("refr_thin_walled").set("1")

            # if textureData["type"] in gammaEnabled:
            #     textureNode.parm("tex0_gammaoverride").set(1)

            if textureData["type"] == "roughness":
                rampNode = materialContainer.createNode("redshift::RSRamp")
                rampNode.setNamedInput("input", triNode, "outColor" )                
                shaderNode.setNamedInput(textureParams["input"], rampNode, textureParams["output"])

            elif textureData["type"] == "opacity":
                spriteNode = materialContainer.createNode("redshift::Sprite")
                spriteNode.setNamedInput("input", shaderNode, "outColor")
                materialNode.setNamedInput("Surface", spriteNode, "outColor")
                spriteNode.parm("tex0").set(textureData["path"].replace("\\", "/"))
                spriteNode.parm("tex0_colorSpace").set("Raw")

            elif textureData["type"] == "metalness":
                channelSplitter2 = materialContainer.createNode("redshift::RSColorSplitter")
                shaderNode.setNamedInput(textureParams["input"], channelSplitter2, textureParams["output"])
                channelSplitter2.setNamedInput("input", triNode, "outColor" )

            elif textureData["type"] == "normal":
                normalNode = materialContainer.createNode("redshift::BumpMap")
                normalNode.parm("inputType").set("1")                

                shaderNode.setNamedInput(textureParams["input"], normalNode, textureParams["output"])
                normalNode.setNamedInput("input", triNode, "outColor")
                normalPriority = True                
                

            elif textureData["type"] == "bump":
                bumpNode = materialContainer.createNode("redshift::BumpMap")                
                if normalPriority == False:
                    shaderNode.setNamedInput(textureParams["input"], bumpNode, textureParams["output"])   
                bumpNode.setNamedInput("input", triNode, "outColor")              
            

            elif textureData["type"] == "displacement":
                exrPath = getExrDisplacement(textureData["path"])                
                textureNode.parm("tex0").set(exrPath.replace("\\", "/"))
                dispNode = materialContainer.createNode("redshift::Displacement")
                dispNode.parm("newrange_min").set(-0.5)
                dispNode.parm("newrange_max").set(0.5)
                


                materialNode.setNamedInput(textureParams["input"], dispNode, textureParams["output"])
                dispNode.setNamedInput("texMap", triNode, "outColor")

            elif textureData["type"] == "albedo" or textureData["type"] == "diffuse":
                ccNode = materialContainer.createNode("redshift::RSColorCorrection")
                ccNode.setNamedInput("input", triNode, "outColor")
                shaderNode.setNamedInput("base_color", ccNode, "outColor")

              

            else:                
                shaderNode.setNamedInput(textureParams["input"], triNode, textureParams["output"])


            hou.node(importParams["materialPath"]).layoutChildren()

       



def registerMaterials():
    
    # materialTypes = ["Principled", "Triplanar"]
    redshiftTextures = RedshiftMaterialFactory()
    redshiftTriplanar = RedshiftTriplanarFactory()
    materialsCreator = MaterialsCreator()
    materialsCreator.registerMaterial("Redshift", "Redshift Material", redshiftTextures.createMaterial)
    materialsCreator.registerMaterial("Redshift", "Redshift Triplanar", redshiftTriplanar.createMaterial)
    

registerMaterials()
