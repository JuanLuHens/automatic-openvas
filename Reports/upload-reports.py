
#Installing boto3 pip3 install boto3
import boto3
import awscli
import os.path
from botocore.exceptions import ClientError
import sys


s3bucket = ""

#fileList2 = ["/home/redteam/gvm/Reports/exports/2024_02_07_15_19_CVE.csv"]
fileList = sys.argv[1:]

aws_access_key_id=''
aws_secret_access_key=''




def awsResource():
    global aws_access_key_id, aws_secret_access_key
    session = boto3.Session(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    return session

def awsConnect():
    global accessKey, secretKey
    awsconnect=boto3.client('s3',region_name='us-west-2',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    return awsconnect

def listbucket(s3bucket):
    session = awsResource()
    s3 = session.resource('s3')
    try:
        my_bucket = s3.Bucket(s3bucket)
        for my_bucket_object in my_bucket.objects.all():
            #print(my_bucket_object.key)
            for file_name in fileList:
                file=os.path.basename(file_name)
                if file in my_bucket_object.key:
                    print(f"El fichero '{file}' se encuentra en el objeto '{my_bucket_object.key}'")
    except Exception as error:
        print (error)  


def uploadfile(s3bucket, filelist):
    s3=awsConnect()
    for file_name in filelist:
        print("Uploading filename {0} ...", file_name)
        try:
            test = s3.upload_file(file_name,s3bucket,"connectors/190/205/6d68d695-48f9-435a-90a7-8eada9b82f28/"+os.path.basename(file_name))
            print("Success")    
        except Exception as error:
            print (error)



if __name__ == '__main__':
    uploadfile(s3bucket, fileList)
    listbucket(s3bucket)
