from __future__ import print_function
import boto3
import os
import sys
from botocore.vendored import requests
import datetime
     
s3_client = boto3.client('s3')
s3 = boto3.resource("s3")
     
def get_data(id):
  headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en',
        'apikey': 'eJe0RTSt2DJ5DSWx2pM5LZK3flh5qDbX'
  }
  return requests.get('https://airapi.airly.eu/v2/measurements/installation?indexType=AIRLY_CAQI&installationId=' + id, headers=headers)
  
def get_installations_ids():
  ids = s3_client.get_object(Bucket='airly', Key='/parameters/ids.txt')
  return ids['Body'].read().decode('utf-8')
  
def save_data_to_s3(r, id, today):
  s3_path = '/tmp/{}/{}'.format(today.strftime("%Y_%m_%d"), id + '.txt')
  s3.Bucket('airly').put_object(Key=s3_path, Body=str(r.json()))

def handler(event, context):
  today = datetime.datetime.now()
  for id in get_installations_ids().split(',')[event['start']:event['stop']]:
    r = get_data(id)
    save_data_to_s3(r, id, today)


