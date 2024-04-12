# megascan_houdini20.0_USD_plugin
Modified Megascans plugin for Houdini 20.0
This is a modification to the Houdini Megascans plugin (Windows) so that you can import variants and assets using the component builder method (Solaris). You will need to install Quixel Bridge to use this mod
This also has added support for mtlx with karma and Redshift

## Megascans 4.6 Installation for Houdini 20.0
Open Quixel Bridge and download the Houdini plugin by going to Edit > Manage Plugins > Houdini 4.6 and download the plugin
As this is not a valid version for 20.0 you will have to manually point to the plugin in your Houdini 20.0 .env file or copy the old MegascansPlugin.json (might be in documents > Houdini20.0 > packages if you install for a previous version) into your packages folder in documents > Houdini20.0
If you do not have any of these manually create a packages folder and add the MegascansPlugin.json
Modify the .json file to point to the install location for your MSLiveLink
Launch Houdini 20.0 and check that Megascans is available in the upper tabs
import an asset to check if the plugin works

## Mod Installation
Create an orig folder and create a backup of all the files you will modify
in C:\MegaScan\Library\support\plugins\houdini\4.6\MSLiveLink\scripts\python\MSPlugin and replace the whole folder
This should now create extra component builder nodes with all the variants connected as well as create mtlx materials in Solaris.
All Redshift materials have been updated for standard shader and USD. Also, make textures visible in the viewport.
