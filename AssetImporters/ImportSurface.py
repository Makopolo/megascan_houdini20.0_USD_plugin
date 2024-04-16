

from ..Utilities.SingletonBase import Singleton
from ..MaterialsSetup.MaterialsCreator import MaterialsCreator
from ..MaterialsSetup import *
import hou, os

from six import with_metaclass

class ImportSurface(with_metaclass(Singleton)):

    def __init__(self):
        pass
    
    def parm_exist(parmpath):
        nodepath, parmname = os.path.split(parmpath)
        node = hou.node(nodepath)
        return node.parmTuple(parmname) != None

    def importAsset(self, assetData, importOptions, importParams):
        
        # asset import parameters
        materialsCreator = MaterialsCreator()
        importedSurface = None
        if not importOptions["UI"]["ImportOptions"]["EnableUSD"]:
            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Karma" :
                pass
            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Redshift" :
                redshiftContainer = hou.node(importParams["materialPath"]).createNode("redshift_vopnet", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = redshiftContainer.path()
                albedoPath = str(hou.node(redshiftContainer.path() + "/albedo"))

                ##############################################

                # print(assetData)
                # print("################")
                # print(importOptions)
                # print("################")
                # print(importParams)

                nodeParams = hou.node(str(redshiftContainer.path()))
                nodeParamsGroups = nodeParams.parmTemplateGroup()
                expA = "`chs(\"albedo/tex0\")`"
                expB = "`chs(\"displacement/tex0\")`"
                expC = "`chs(\"Sprite1/tex0\")`"

                nodeTexParam = hou.FolderParmTemplate(
                "rstexs",
                "RS Textures",
                folder_type=hou.folderType.Simple,
                    parm_templates=[
                        hou.FloatParmTemplate("rs_tex_uvscale1", "Scale", 2, default_expression=("ch(\"albedo/scale1\")", "ch(\"albedo/scale2\")"), default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                        hou.FloatParmTemplate("rs_tex_uvtranslate1", "Offset", 2, default_expression=("ch(\"albedo/offset1\")", "ch(\"albedo/offset2\")"), default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                        hou.FloatParmTemplate("rs_tex_uvrotate1", "Rotate", 1, default_expression=[("ch(\"albedo/rotate\")")], default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                        hou.ToggleParmTemplate("ogl_use_tex1", "Display Texture", default_value=True)
                        

                    ]
                )
                nodeAddParam = hou.FolderParmTemplate(
                                "ogltexs",
                                "OGL Textures",
                                folder_type=hou.folderType.Simple,
                                    parm_templates=[
                                        hou.StringParmTemplate("ogl_tex1", "Texture", 1, [expA]),
                                        hou.StringParmTemplate("ogl_opacitymap", "Alpha", 1, [expC]),
                                        hou.FloatParmTemplate("ogl_tex_uvscale1", "Scale", 2, default_expression=("1/ch(\"albedo/scale1\")", "1/ch(\"albedo/scale2\")"), default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                                        hou.FloatParmTemplate("ogl_tex_uvtranslate1", "Offset", 2, default_expression=("ch(\"albedo/offset1\")", "ch(\"albedo/offset2\")"), default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                                        hou.FloatParmTemplate("ogl_tex_uvrotate1", "Rotate", 1, default_expression=[("ch(\"albedo/rotate\")")], default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript))
                                        
                                        

                                    ]
                                )

                nodeAddDispParam = hou.FolderParmTemplate(
                                "ogltexs",
                                "OGL Displacement",
                                folder_type=hou.folderType.Simple,
                                    parm_templates=[
                                        hou.ToggleParmTemplate("ogl_use_displacemap", "Displace", default_value=False),
                                        hou.FloatParmTemplate("ogl_displacescale", "Displace Scale", 1, default_expression=[("ch(\"Displacement1/scale\")")], default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                                        hou.FloatParmTemplate("ogl_displaceoffset", "Displace Offset", 1, default_expression=[("ch(\"Displacement1/newrange_min\")")], default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                                        hou.StringParmTemplate("ogl_displacemap", "Texture", 1, [expB]),
                                        hou.FloatParmTemplate("ogl_displace_uvscale", "UV Scale", 2, default_expression=("1/ch(\"displacement/scale1\")", "1/ch(\"displacement/scale2\")"), default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                                        hou.FloatParmTemplate("ogl_displace_uvtranslate", "UV Offset", 2, default_expression=("ch(\"displacement/offset1\")", "ch(\"displacement/offset2\")"), default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript)),
                                        hou.FloatParmTemplate("ogl_displace_uvrotate", "UV Rotate", 1, default_expression=[("ch(\"displacement/rotate\")")], default_expression_language=(hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript, hou.scriptLanguage.Hscript))
                                        
                        
                                    ]
                                )

                nodeParamsGroups.append(nodeTexParam)
                nodeParamsGroups.append(nodeAddDispParam)
                nodeParamsGroups.append(nodeAddParam)
                redshiftContainer.setParmTemplateGroup(nodeParamsGroups)
            #else:
                    #pass

            elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Arnold":
                arnoldContainer = hou.node(importParams["materialPath"]).createNode("arnold_materialbuilder", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = arnoldContainer.path()

            elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Octane":
                octaneContainer = hou.node(importParams["materialPath"]).createNode("octane_vopnet", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = octaneContainer.path()

            elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Renderman":
                rendermanContainer = hou.node(importParams["materialPath"]).createNode("pxrmaterialbuilder", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = rendermanContainer.path()


            importedSurface = materialsCreator.createMaterial(importOptions["UI"]["ImportOptions"]["Renderer"], importOptions["UI"]["ImportOptions"]["Material"], assetData, importParams, importOptions)
            
            hou.node(importParams["materialPath"]).moveToGoodPosition()


            hou.node("/mat").moveToGoodPosition()
            
            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Arnold":
                return arnoldContainer

            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Octane":
                return octaneContainer

            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Redshift":
                return redshiftContainer

            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Renderman":
                hou.node(importParams["materialPath"]).layoutChildren()
                return rendermanContainer
            importedSurface.setSelected(True)
            return importedSurface
        
        elif importOptions["UI"]["ImportOptions"]["EnableUSD"] and importParams["importType"] == "Normal" :
            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Redshift" :
                redshiftContainer = hou.node(importParams["materialPath"]).createNode("redshift_vopnet", node_name=importParams["assetName"], run_init_scripts=False)
                
                importParams["materialPath"] = redshiftContainer.path()

            elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Arnold":
                arnoldContainer = hou.node(importParams["materialPath"]).createNode("arnold_materialbuilder", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = arnoldContainer.path()

            elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Octane":
                octaneContainer = hou.node(importParams["materialPath"]).createNode("octane_vopnet", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = octaneContainer.path()

            elif importOptions["UI"]["ImportOptions"]["Renderer"] == "Renderman":
                rendermanContainer = hou.node(importParams["materialPath"]).createNode("pxrmaterialbuilder", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = rendermanContainer.path()


            importedSurface = materialsCreator.createMaterial(importOptions["UI"]["ImportOptions"]["Renderer"], importOptions["UI"]["ImportOptions"]["Material"], assetData, importParams, importOptions)
            
            hou.node(importParams["materialPath"]).moveToGoodPosition()


            hou.node("/mat").moveToGoodPosition()
            
            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Arnold":
                return arnoldContainer

            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Octane":
                return octaneContainer

            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Redshift":
                return redshiftContainer

            if importOptions["UI"]["ImportOptions"]["Renderer"] == "Renderman":
                hou.node(importParams["materialPath"]).layoutChildren()
                return rendermanContainer
            
            importedSurface.setSelected(True)
            return importedSurface
            ##########################################
            #
            #      Modified section
            #
            ##########################################
        
        
        
        else:
            usdMaterials = {"Karma" : "Karma", "Renderman" : "Pixar Surface", "Arnold" : "Standard Surface", "Redshift_USD" : "Redshift_USD"}
            usdRendererType = importOptions["UI"]["USDOptions"]["USDMaterial"]


            if assetData["type"] == "surface" or assetData["type"] == "atlas" and not importOptions["UI"]["ImportOptions"]["UseAtlasSplitter"] or assetData["type"] == "brush":
                usdMaterialContainer = hou.node(importParams["materialPath"]).createNode("materiallibrary", importParams["assetName"])
                importParams["materialPath"] = usdMaterialContainer.path()

            if usdRendererType == "Karma":
                usdRendererType = "Mantra"
                if not importOptions["UI"]["ImportOptions"]["UseAtlasSplitter"] or assetData["type"]=="3d":
                    usdRendererType = "Karma"
                    karmaContainer = hou.node(importParams["materialPath"]).createNode("subnet", node_name=importParams["assetName"])
                    importParams["materialPath"] = karmaContainer.path()
            
            


            if importOptions["UI"]["USDOptions"]["USDMaterial"] == "Redshift_USD":
                importOptions["UI"]["USDOptions"]["Material"] = "Redshift Material"
                importOptions["UI"]["USDOptions"]["Renderer"] = "Redshift"
                redshiftContainer = hou.node(importParams["materialPath"]).createNode("rs_usd_material_builder", node_name=importParams["assetName"])
                importParams["materialPath"] = redshiftContainer.path()
    

            if importOptions["UI"]["USDOptions"]["USDMaterial"] == "Arnold":
                arnoldContainer = hou.node(importParams["materialPath"]).createNode("arnold_materialbuilder", node_name=importParams["assetName"], run_init_scripts=False)
                importParams["materialPath"] = arnoldContainer.path()
            
            if importOptions["UI"]["ImportOptions"]["USDmatLoop"]==True and usdRendererType == "Mantra":
                usdRendererType = "Karma"
                karmaContainer = hou.node(importParams["materialPath"]).createNode("subnet", node_name=importParams["assetName"])
                importParams["materialPath"] = karmaContainer.path()


            # if importOptions["UI"]["ImportOptions"]["Renderer"] == "Karma" and importOptions["UI"]["ImportOptions"]["EnableUSD"]:
            #     importOptions["UI"]["ImportOptions"]["Renderer"] = "Karma"
            #     importOptions["UI"]["ImportOptions"]["Material"] = "Karma"
            #     importOptions["UI"]["ImportOptions"]["USDmatLoop"] = True
            
            importedSurface = materialsCreator.createMaterial(usdRendererType, usdMaterials[usdRendererType], assetData, importParams, importOptions)
            if importOptions["UI"]["USDOptions"]["USDMaterial"] == "Arnold" :
                dispValue = "0.008"
                if assetData["type"] == "surface" or assetData["type"] == "atlas":                    
                    for assetMeta in assetData["meta"]:
                        if assetMeta["key"] == "height":
                            dispValue = assetMeta["value"].split(" ")[0]
                
                    renderSettings = usdMaterialContainer.createOutputNode("rendergeometrysettings")
                    renderSettings.parm("arnolddisp_height_control")#.set("set")                    
                    renderSettings.parm("xn__primvarsarnolddisp_height_uhbg").set(dispValue)
                    
                importedSurface = arnoldContainer

            if assetData["type"] == "surface" or assetData["type"] == "atlas" and not importOptions["UI"]["ImportOptions"]["UseAtlasSplitter"] or assetData["type"] == "brush":
                usdMaterialContainer.parm("matnode1").set(importParams["assetName"])
                usdMaterialContainer.parm("matpath1").set(importParams["assetName"])

            hou.node(importParams["materialPath"]).moveToGoodPosition()
            hou.node("/mat").moveToGoodPosition()
            importedSurface.setSelected(True)

            return importedSurface




        
            
        
        
