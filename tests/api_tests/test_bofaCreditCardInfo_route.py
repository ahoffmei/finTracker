import requests
import json 

LOCAL_HOST = r'http://127.0.0.1:5000/bofaCreditCardInfo' 

def testUploadBofaCcDataExcel(base_url):
    url = base_url + "/uploadBofaCcDataCsv"
    with open(r"C:\Users\Adam\Downloads\November2025_5226.csv", 'rb') as f: 
        files = {"file": f}
        response = requests.post(url, files=files)

    print(response.json())


def testTest(base_url): 
    url = base_url+ "/test"
    response = requests.get(url)
    print(response.text)


testTest(LOCAL_HOST)
testUploadBofaCcDataExcel(LOCAL_HOST)