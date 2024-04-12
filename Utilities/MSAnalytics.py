import json,socket,requests
import hou

class MSAnalytics:
    def __init__(self, importOptions, assetData, HOUDINI_PLUGIN_VERSION):        
        self.HOUDINI_PLUGIN_VERSION =  HOUDINI_PLUGIN_VERSION
        self.logData = self.getLogData(importOptions, assetData)
        self.port = self.getPort()
        
    def getPort(self):    
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 28852        # Port to listen on (non-privileged ports are > 1023)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        activeport = sock.recv(32)
        sock.close()
        return activeport.decode("utf-8") 

    def getLogData(self,importOptions, assetData):
        data = {
            "event": "HOUDINI_ASSET_IMPORT",
            "data" : { 
                "guid": assetData['guid'],
                "asset_ID": assetData['id'],          
                "houdini_version" : hou.applicationVersionString(),
                "renderer" : importOptions["UI"]["ImportOptions"]["Renderer"],
                "plugin_version" : self.HOUDINI_PLUGIN_VERSION,
                "material_type" :importOptions["UI"]["ImportOptions"]["Material"],
                "usd_enabled" : importOptions["UI"]["ImportOptions"]["EnableUSD"],
                "UseAtlasSplitter" : importOptions["UI"]["ImportOptions"]["UseAtlasSplitter"],
                "EnableLods" : importOptions["UI"]["ImportOptions"]["EnableLods"],
                "ApplyMotion" : importOptions["UI"]["ImportOptions"]["ApplyMotion"],
                "ConvertToRAT" : importOptions["UI"]["ImportOptions"]["ConvertToRAT"]
            }             
        }
        return data

    def sendAnalytics (self):
        self.sendToMetabase()
        self.sendToBridgeLog()        
        
    def sendToMetabase (self):
        url ="http://localhost:" + self.port+ "/analytics/"
        requests.post(url, data= json.dumps(self.logData))

    def sendToBridgeLog(self):
        url = "http://localhost:" + self.port + "/log/"
        requests.post(url, data= json.dumps(self.logData))