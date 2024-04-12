

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
        smNode =  str(materialContainer.path()) + "/StandardMaterial1"
        rsmatOUT = str(hou.node(materialPath).path()) + "/" + "redshift_usd_material1"

        uvNode = materialContainer.createNode("usdprimvarreader")
        uvNode.parm("signature").set("float2")
        uvNode.parm("varname").set("st")
        uvTransNode = materialContainer.createNode("usdtransform2d")
        uvTransNode.setNamedInput("in", uvNode, "result")

        usdPrevShader = materialContainer.createNode("usdpreviewsurface")
        subOutPath =   str(materialContainer.path()) + "/suboutput1"
        shaderNode = materialContainer.node(smNode)
        materialNode = materialContainer.node(rsmatOUT)
        subOutNode = materialContainer.node(subOutPath)

        subOutNode.setInput(1,usdPrevShader, 0)

        normalPriority = False      
        isAlbedoPath = None
        for textureData in assetData["components"]:

            if textureData["type"] != "opacity":
                textureNode = materialContainer.createNode("redshift::TextureSampler", textureData["type"])
                textureNode.parm("tex0").set(textureData["path"].replace("\\", "/"))
                usdPreviewTex = materialContainer.createNode("usduvtexture::2.0", textureData["type"])
                usdPreviewTex.setNamedInput("st", uvTransNode, "result")
                usdPreviewTex.parm("file").set(textureData["path"].replace("\\", "/"))


                if textureData["type"] == "albedo":
                    textureNode.parm("tex0_colorSpace").set("sRGB")
                    albedoOffPath = "ch(\"" + str(textureNode.path()) 
                    textureNode.parm("scale2").setExpression(albedoOffPath + "/scale1\")" )
                    usdPreviewTex.parm("sourceColorSpace").set("sRGB")
                    usdPreviewTex.parm("scaler").set(1)
                    usdPreviewTex.parm("scaleg").set(1)
                    usdPreviewTex.parm("scaleb").set(1)


                    
                    isAlbedoPath = True
                else:
                    textureNode.parm("tex0_colorSpace").set("Raw")
                    if isAlbedoPath == True:
                        textureNode.parm("scale1").setExpression(albedoOffPath + "/scale1\")" )
                        textureNode.parm("scale2").setExpression(albedoOffPath + "/scale2\")" )
                        textureNode.parm("offset1").setExpression(albedoOffPath + "/offset1\")" )
                        textureNode.parm("offset2").setExpression(albedoOffPath + "/offset2\")" )
                        textureNode.parm("rotate").setExpression(albedoOffPath + "/rotate\")" )
                        usdPreviewTex.parm("sourceColorSpace").set("raw")

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
                usdPreviewTex = materialContainer.createNode("usduvtexture::2.0", textureData["type"])
                usdPreviewTex.setNamedInput("st", uvTransNode, "result")
                usdPreviewTex.parm("file").set(textureData["path"].replace("\\", "/"))
                usdPrevShader.setNamedInput("opacity",usdPreviewTex,"r")


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
                usdPreviewTex.parm("scaler").set(0.1)
                usdPreviewTex.parm("scaleg").set(0.1)
                usdPreviewTex.parm("scaleb").set(0.1)


                materialNode.setNamedInput(textureParams["input"], dispNode, textureParams["output"])
                dispNode.setNamedInput("texMap", textureNode, "outColor")

            elif textureData["type"] == "albedo" or textureData["type"] == "diffuse":
                ccNode = materialContainer.createNode("redshift::RSColorCorrection")
                ccNode.setNamedInput("input", textureNode, "outColor")
                shaderNode.setNamedInput("base_color", ccNode, "outColor")
                usdPrevShader.setNamedInput("diffuseColor",usdPreviewTex,"rgb")

              

            else:                
                shaderNode.setNamedInput(textureParams["input"], textureNode, textureParams["output"])


            hou.node(importParams["materialPath"]).layoutChildren()
                
        if isAlbedoPath == True:
            uvTransNode.parm("scale1").setExpression(albedoOffPath + "/scale1\")" )
            uvTransNode.parm("scale2").setExpression(albedoOffPath + "/scale2\")" )
            uvTransNode.parm("translation1").setExpression(albedoOffPath + "/offset1\")" )
            uvTransNode.parm("translation2").setExpression(albedoOffPath + "/offset2\")" )
            uvTransNode.parm("rotation").setExpression(albedoOffPath + "/rotate\")" )
            
           
        
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
    redshiftTextures = RedshiftMaterialFactory()
    redshiftTriplanar = RedshiftTriplanarFactory()
    materialsCreator = MaterialsCreator()
    materialsCreator.registerMaterial("Redshift_USD", "Redshift_USD", redshiftTextures.createMaterial)
    

registerMaterials()
