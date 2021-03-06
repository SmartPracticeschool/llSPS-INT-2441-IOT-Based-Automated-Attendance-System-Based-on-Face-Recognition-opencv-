# -*- coding: utf-8 -*-

import datetime
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import cv2
import numpy as np
import sys
import ibmiotf.application
import ibmiotf.device
import random
import time
import json

from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from cloudant.client import Cloudant
from cloudant.error import CloudantException 
from cloudant.result import Result, ResultByKey
#Provide your IBM Watson Device Credentials
organization = "uxl664"
deviceType = "iot"
deviceId = "015"
authMethod = "token"
authToken = "6303898175"



def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data)
        print(cmd.data['command'])
       
        if(cmd.data['command']=="open"):
                print("door open")
                
        if(cmd.data['command']=="close"):
                print("door close")
                

        if(cmd.data['command']=="lighton"):
                print("light on")
                
        if(cmd.data['command']=="lightoff"):
                print("light off")
               
        if(cmd.data['command']=="present"):
                print("present")
        if(cmd.data['command']=="absent"):
                print("absent")

try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
	#..............................................
	
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()
face_classifier=cv2.CascadeClassifier("haar-face.xml")


#It will read the first frame/image of the video
video=cv2.VideoCapture('video3.mp4')



COS_ENDPOINT = "https://s3.us.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "75EFmi6-6DPQVMknKBchXOdQQqa2mHmorb7nWGQPVzwj" # eg "W00YiRnLW4a3fTjMB-oiB-2ySfTrFBIQQWanc--P3byk"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/e7faebd9d761480bb961b30b6eda9b91:92440559-bf42-49b9-8ea2-267eed9d2bda::"

client = Cloudant("8e7237b7-402b-4171-a550-9af9eda65bf6-bluemix", "9dc4ca6821a0f866d4527339c89a0e15323c8e95b6a0bc15d2cd28df6df6ced9", url="https://8e7237b7-402b-4171-a550-9af9eda65bf6-bluemix:9dc4ca6821a0f866d4527339c89a0e15323c8e95b6a0bc15d2cd28df6df6ced9@8e7237b7-402b-4171-a550-9af9eda65bf6-bluemix.cloudantnosqldb.appdomain.cloud")
client.connect()
database_name = "doorbell"

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)
        
        
def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))
        
authenticator = IAMAuthenticator('p94o5iYZ4Yy_mJBsjKJMDWOcpgQpKb1ThS667EYS5GiL')
visual_recognition = VisualRecognitionV3(
    version='2018-03-19',
    authenticator=authenticator
)

visual_recognition.set_service_url('https://api.us-south.visual-recognition.watson.cloud.ibm.com/instances/5da92653-bc4d-400d-8163-5c0602441914')
       
while True:
    #capture the first frame
    check,frame=video.read()
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #detect the faces from the video using detectMultiScale function
    faces=face_classifier.detectMultiScale(gray,1.3,5)
    
    
    #drawing rectangle boundries for the detected face
    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (127,0,255), 2)
        cv2.imshow('Face detection', frame)
        picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        picname=picname+".jpg"
        pic=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        datetym=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        cv2.imwrite(picname,frame)
        with open(picname, 'rb') as images_file:
            classes = visual_recognition.classify(
                images_file=images_file,
                threshold='0.6',classifier_ids='DefaultCustomModel_1112676152').get_result()
            print(json.dumps(classes, indent=2))
            person1=classes['images'][0]['classifiers'][0]['classes'][0]['class']
            print("person1")
            print(person1)
            if(person1=="sachin.zip"):
                    person1="Sachin"

                  
        person=1
        my_database = client.create_database(database_name)        
        multi_part_upload("project-donotdelete-pr-7irtazedott6ek",picname,pic+".jpg")      
        if my_database.exists():
            print("'{database_name}' successfully created.")
            json_document = {
                    "_id": pic,
                    "link":COS_ENDPOINT+"/project-donotdelete-pr-7irtazedott6ek/"+picname
                    }
            new_document = my_database.create_document(json_document)
            if new_document.exists():
                print("Document '{new_document}' successfully created.")
        time.sleep(1)
        p=34
        data = {"d":{ 'present' : p, 'person': person1,'datetym':datetym}}
        #print data
        def myOnPublishCallback():
            print ("Published data to IBM Watson")

        success = deviceCli.publishEvent("Data", "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
            print("Not connected to IoTF")
        time.sleep(1)
        deviceCli.commandCallback = myCommandCallback
        person=0
        




    #waitKey(1)- for every 1 millisecond new frame will be captured
    Key=cv2.waitKey(1)
    if Key==ord('q'):
        #release the camera
            video.release()
        #destroy all windows
            cv2.destroyAllWindows()
            break
deviceCli.disconnect()
    
