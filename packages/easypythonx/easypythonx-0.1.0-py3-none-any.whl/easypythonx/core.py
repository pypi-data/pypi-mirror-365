import requests
import urllib3
import boto3
import subprocess
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Simple GET request using requests
def get_url(url):
    try:
        res = requests.get(url)
        return res.text
    except Exception as e:
        return f"[get_url error] {e}"

# Manual urllib3 request
def make_request(url):
    try:
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        return r.data.decode()
    except Exception as e:
        return f"[make_request error] {e}"

# Upload a file to S3
def boto_upload(bucket_name, file_path, object_name=None):
    try:
        s3 = boto3.client('s3')
        if object_name is None:
            object_name = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, object_name)
        return f"✅ Uploaded {file_path} to s3://{bucket_name}/{object_name}"
    except Exception as e:
        return f"[boto_upload error] {e}"

# Compile Python script to .exe using PyInstaller
def compile_to_exe(script_path):
    try:
        subprocess.run(["pyinstaller", "--onefile", script_path], check=True)
        return f"✅ EXE built for {script_path}"
    except Exception as e:
        return f"[compile_to_exe error] {e}"
