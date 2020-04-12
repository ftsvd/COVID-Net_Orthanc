import numpy as np
import tensorflow as tf
import os, argparse, time
import urllib
from urllib.request import urlopen
import cv2
import requests
import json
import base64

# COVID-Net model prediction mapping
mapping = {'normal': 0, 'pneumonia': 1, 'COVID-19': 2}
reversemapping = {0: 'normal', 1: 'pneumonia', 2: 'COVID-19'}

# These are required tags for pushing new DICOM instance holding the prediction into PACS
mandatorytags = ["PatientName","PatientID","SOPClassUID","SOPInstanceUID","Modality","SeriesDescription","StudyDate","SeriesDate","StudyTime","SeriesTime","SpecificCharacterSet","ImageType","AcquisitionDate","AcquisitionTime","ContentDate","ContentTime","InstanceCreationDate","InstanceCreationTime","StudyInstanceUID","SeriesInstanceUID","AccessionNumber","ConversionType","Manufacturer","PatientBirthDate","PatientSex","ReferringPhysician","DeviceSerialNumber","SeriesNumber","InstanceNumber","PatientOrientation","Laterality","PixelData"]

def eval(sess, graph, orthancinstance):
    image_tensor = graph.get_tensor_by_name("input_1:0")
    pred_tensor = graph.get_tensor_by_name("dense_3/Softmax:0")

    # ORTHANC BASE URL
    orthanc = "http://localhost:8052/"

    # LOAD INSTANCE TAGS FROM URL
    url = orthanc + "instances/" + orthancinstance + "/simplified-tags"
    resp = requests.get(url)
    originaltags = resp.json()

    # COPY MANDATORY TAGS FROM ORIGINAL DICOM TO NEW DICOM
    newtags = dict()
    for tag in mandatorytags:
        # create empty tags if original DICOM file does not have that tag
        if not tag in originaltags:
            originaltags[tag] = ""
        newtags[tag] = originaltags[tag]
        
    # modify instance-specific tags to allow predictions to be displayed within the same study in PACS
    newtags["SeriesInstanceUID"] = newtags["SeriesInstanceUID"] + ".1"
    newtags["SeriesDescription"] = "COVID-Net Prediction"
    newtags["SOPInstanceUID"] = newtags["SOPInstanceUID"] + ".1"
    newtags["Modality"] = "OT"

    # LOAD PNG FROM URL
    url = orthanc + "instances/" + orthancinstance + "/preview"
    resp = urlopen(url)
    x = np.asarray(bytearray(resp.read()), dtype="uint8")
    x = cv2.imdecode(x, cv2.IMREAD_COLOR)
    x = cv2.resize(x, (224, 224))
    thumbnail = x
    x = x.astype('float32') / 255.0

    # PREDICT FROM PNG
    pred = np.array(sess.run(pred_tensor, feed_dict={image_tensor: np.expand_dims(x, axis=0)})).argmax(axis=1)
    pred = pred.astype(int)[0]

    # PUSH PREDICTION TO ORTHANC
    
    # Draw Prediction PIXELDATA
    # black blank image
    image = np.zeros(shape=[512, 512, 3], dtype=np.uint8)
    
    # draw thumbnail
    image[10:234, 10:234] = thumbnail
    
    # font parameters
    font = cv2.FONT_HERSHEY_SIMPLEX 
    fontScale = 0.5
    color = (255, 255, 255) #BGR
    thickness = 1
    
    image = cv2.putText(image, 'COVID-Net Prediction', (10, 250), font, fontScale, color, thickness, cv2.LINE_AA)
    image = cv2.putText(image, '(EXPERIMENTAL USE ONLY)', (10, 270), font, fontScale, color, thickness, cv2.LINE_AA)
    image = cv2.putText(image, newtags["PatientName"], (10, 310), font, fontScale, color, thickness, cv2.LINE_AA)
    image = cv2.putText(image, newtags["PatientID"], (10, 330), font, fontScale, color, thickness, cv2.LINE_AA)
    image = cv2.putText(image, newtags["StudyDate"], (10, 350), font, fontScale, color, thickness, cv2.LINE_AA)
    image = cv2.putText(image, "Prediction: " + reversemapping[pred], (10, 390), font, fontScale, color, thickness, cv2.LINE_AA)

    retval, buffer= cv2.imencode('.png', image)
    imageb64 = base64.b64encode(buffer)
    imageb64 = imageb64.decode("utf-8")
    imageb64 = 'data:image/png;base64,' + imageb64
    
    newtags["PixelData"] = imageb64
    url = orthanc + "tools/create-dicom"
    r = requests.post(url, json.dumps(newtags))
    print(r.text)

if __name__ == '__main__':

    # Path to output folder
    weightspath = "model"
    
    # Name of ckpt meta file
    metaname = "model.meta_eval" 
    
    # Name of model ckpts
    ckptname = "model-6207"
    
    # LOAD TRAINED MODEL INTO SESSION
    sess = tf.Session()
    tf.get_default_graph()
    saver = tf.train.import_meta_graph(os.path.join(weightspath, metaname))
    saver.restore(sess, os.path.join(weightspath, ckptname))
    graph = tf.get_default_graph()

    # MAIN LOOP - POLL FOLDER WHERE NEW INSTANCE WILL BE LISTED BY ORTHANC
    folder = "orthanc157/InstanceToBePredicted"
    print("Waiting for Instances")
    while 1:
        time.sleep(5)
        for file in os.listdir(folder):
            print("Predicting Instance: " + file)
            orthancinstance = file
            eval(sess, graph, orthancinstance)
            os.remove(os.path.join(folder,file))        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        