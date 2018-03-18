#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib, urllib, base64, json
import configparser
config = configparser.ConfigParser()
config.read('cfg.ini')

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': config['MSFACE']['api_key'],
}

# create a person group with name users
personGroupId = 'users'
msface_api_url = 'westcentralus.api.cognitive.microsoft.com'

def face_detect(image_url):
    params =urllib.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false'
    })

    body = '{"url":"%s"}'% image_url
    try:
        conn = httplib.HTTPSConnection(msface_api_url)
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        obj = json.loads(data)
        #print obj[0]['faceId']
        return obj[0]['faceId']
    except Exception as e:
        print("Error: %s" % e.message)



def create_person_group():
    params = urllib.urlencode({
    'personGroupId' :  personGroupId
    })

    body = '{}'
    try:
        conn = httplib.HTTPSConnection(msface_api_url)
        conn.request("PUT", "/face/v1.0/persongroups/{personGroupId}?%s" % params,body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("Error: %s" % e.message)





def get_persons():

    try:
        conn = httplib.HTTPSConnection(msface_api_url)
        conn.request("GET", "/face/v1.0/persongroups/%s/persons?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        persons=[]
        for row in data:
            persons.append({'name':row['name'],'personId':row['personId']})
        conn.close()

        return persons
    except Exception as e:
        print("Error: %s" % e.message)


def create_person(pname,udata):
    params = urllib.urlencode({
        'personGroupId' : personGroupId
    })
    persons=get_persons()
    
    if persons:
        for row in persons:
            if pname == row['name']:
                return row['personId']    
    body = '{"name":"%s","userData":"%s"}' % (pname,udata)
    
    try:
        conn = httplib.HTTPSConnection(msface_api_url )
        conn.request("POST", "/face/v1.0/persongroups/%s/persons?" % personGroupId, body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        conn.close()
        if not data['personId']:
            return ''
        else:    
            return data['personId']
    except Exception as e:
        print("Error: %s" % e.message)        



def add_person_face(personId,image_url):
    body = '{"url":"%s"}'% image_url
    try:
        conn = httplib.HTTPSConnection(msface_api_url)
        conn.request("POST", "/face/v1.0/persongroups/%s/persons/%s/persistedFaces?" %(personGroupId,personId), body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        #print data
        conn.close()
    except Exception as e:
        print(e)    


def face_identify(faceId):
    body = '{ "personGroupId":"%s","faceIds":["%s"]}' % (personGroupId, faceId)
    try:
        conn = httplib.HTTPSConnection(msface_api_url)
        conn.request("POST", "/face/v1.0/identify?" , body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        pid=data[0]['candidates'][0]['personId']
        #print(pid)
        conn.close()
        return pid
    except Exception as e:
        print("Error: %s" % e.message) 

def train():
    try:
        conn = httplib.HTTPSConnection(msface_api_url)
        conn.request("POST", "/face/v1.0/persongroups/%s/train?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("Error: %s" % e.message)      