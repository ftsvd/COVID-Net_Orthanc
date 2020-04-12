# COVID-Net_Orthanc
Integrating COVID-Net with Orthanc

## Purpose
To bring COVID-Net (https://github.com/lindawangg/COVID-Net/) predictions into the clinical environment where the model automatically evaluates every incoming chest radiograph and outputs the predictions in DICOM format back into Orthanc (where it can pushed back into PACS)

## Warning
As the original authors of COVID-Net have put it - this model is far from production-ready. Therefore, any inadvertent effect on clinical outcome due to use of this model is your own responsibility.

The reason I'm doing this is because I need to show my radiology and clinical colleagues the way this AI model can be integrated into the clinical environment to (hopefully) get their support.

## Installation Instructions
1. Read the Warning first
2. Clone this repository
3. Install Orthanc (command line) into the `Orthanc` subfolder.
    - Take note of the DICOM and HTTP ports in `orthanc.json`
    - Add `listInstanceToBePredicted.lua` to the Lua script within `orthanc.json`
        - `"LuaScripts" : [ "../listInstanceToBePredicted.lua" ],`
    - Create an empty folder `InstanceToBePredicted` within `Orthanc`
    - Run Orthanc
4. Run `predictorloop.py`

## How it works
1. Orthanc receives a new chest radiograph in DICOM format (through the DICOM network or uploaded through Orthanc Explorer)
2. On storing this new instance, `listInstanceToBePredicted.lua` is called, which creates a file with the name of the instance UID of the stored instance within the `InstanceToBePredicted` folder.
3. `predictorloop.py` will scan the `InstanceToBePredicted` folder every 5 seconds
4. Once it detects a file there, it will get the name of the file (which is the instance UID of the chest radiograph)
5. `predictorloop.py` will retrieve the PNG of the instance from Orthanc using the `/preview` GET function and run it through the model
6. `predictorloop.py` will prepare a new DICOM instance which holds the prediction, and upload it back to Orthanc using the `tools/create-dicom` POST function
7. At this point, you can see both the radiograph and the prediction in Orthanc Explorer
8. [Additional] Pushing this back to PACS is via a simple autorouting script which can be written in Lua

For further info, I'm at ftsvd@yahoo.com.
