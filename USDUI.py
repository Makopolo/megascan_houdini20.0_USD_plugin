
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class USDOptions(QtWidgets.QWidget):
    def __init__(self, usdOptions, settingsCallback):
        super(USDOptions, self).__init__()
        self.usdOptions = usdOptions
        self.settingsCallback = settingsCallback
        
        self.SetupOptionsW()


    def SetupOptionsW(self):
        self.widgetVBLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.widgetVBLayout)

        self.uiBox = QtWidgets.QGroupBox("USD Options :")        
        self.widgetVBLayout.addWidget(self.uiBox)        

        # Main UI Layout
        self.uiLayout = QtWidgets.QGridLayout()
        self.uiBox.setLayout(self.uiLayout)
        

        # Material type
        materialTypeText = QtWidgets.QLabel("USD Material")
        self.materialTypeDrop = QtWidgets.QComboBox()
        self.materialTypeDrop.setToolTip("Material type to create on USD stage")
        self.uiLayout.addWidget(materialTypeText, 0,0)
        self.uiLayout.addWidget(self.materialTypeDrop, 0, 1)
        usdMaterials = ["Karma", "Renderman", "Arnold","Redshift_USD"] ####modified####
        self.materialTypeDrop.addItems(usdMaterials)

        if self.usdOptions["USDMaterial"] in usdMaterials:
            materialIndex = self.materialTypeDrop.findText(self.usdOptions["USDMaterial"])
            if materialIndex >= 0:
                self.materialTypeDrop.setCurrentIndex(materialIndex)

        self.materialTypeDrop.currentIndexChanged.connect(self.materialChanged)

        self.refpathRegexp = QtCore.QRegExp("[\\/][A-Za-z0-9\\/]+[\\/]")
        refpathValidator = QtGui.QRegExpValidator(self.refpathRegexp)

    def miscOptionChanged(self, optionObject, state):
        optionName = optionObject.objectName()        
        self.usdOptions[optionName] = state
        self.settingsChanged()

    def materialChanged(self, index):
        self.usdOptions["USDMaterial"] = self.materialTypeDrop.itemText(index)
        self.settingsChanged()


    def textInputChanged(self, optionObject):        
        if optionObject.text() == self.usdOptions[optionObject.objectName()]:          
            return

        if self.refpathRegexp.exactMatch(optionObject.text()):
            optionObject.setStyleSheet("border: 1px solid black")
            self.usdOptions[optionObject.objectName()] = optionObject.text()
            self.settingsChanged()
        
        else:
            optionObject.setStyleSheet("border: 1px solid red")          


    def settingsChanged(self):
        
        self.settingsCallback("USDOptions", self.usdOptions)

