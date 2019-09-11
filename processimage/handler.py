import json
from minio import Minio
import requests
import os
import base64

def handle(st):
    
    """handle a request to the function
    Args:
        st (str): request body
    """

    req = json.loads(st)

    gateway = os.environ['openfaas_gw']

    mc = Minio(os.environ['minio_hostname'],
                  access_key=os.environ['minio_access_key'],
                  secret_key=os.environ['minio_secret_key'],
                  secure=False)

    source_bucket = "incoming"
    dest_bucket = "processed"

    file_name = req['Key'].split('/')[-1]
    print(source_bucket, dest_bucket, file_name, mc)

    mc.fget_object(source_bucket, file_name, "/tmp/" + file_name)

    f = open("/tmp/" + file_name, "rb")
    input_image = base64.b64encode(f.read())

    r = requests.post(gateway + "/function/facedetect", input_image)

    dest_file_name = "processed" + file_name
    f = open("/tmp/" + dest_file_name, "wb")
    f.write(r.content)
    f.close()

    f = open("/tmp/input_" + file_name, "wb")
    f.write(input_image)
    f.close()

    # sync to Minio
    mc.fput_object(dest_bucket, dest_file_name, "/tmp/"+dest_file_name)
    
