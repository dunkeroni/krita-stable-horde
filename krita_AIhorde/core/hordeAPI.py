import base64
import json
import ssl
import urllib.request
import urllib.error
import math
import re
from ..misc import utility

API_ROOT = "https://stablehorde.net/api/v2/"
CHECK_WAIT = 5
CLIENT_AGENT = "dunkeroni's crappy Krita plugin"

ssl._create_default_https_context = ssl._create_unverified_context


def status_models(sort = True):
    #get models from stablehorde
    #return list of models if successful, empty list if not
    """ Model List Format:
    [
        {
            "name": "string",
            "count": 0,
            "performance": 0,
            "queued": 0,
            "eta": 0,
            "type": "image"
        }
    ]"""
    try:
        response = urllib.request.urlopen(API_ROOT + "status/models")
        models = json.loads(response.read())

        #sort models based on Count
        if sort:
            models = sorted(models, key=lambda k: k['count'], reverse=True)
    except urllib.error.URLError as e:
        utility.errorMessage("status_models url error", e.reason)
        models = []
    except:
        utility.errorMessage("Error", "Something went wrong while trying to get a list of models.")
        models = []
    return models


def find_user(apikey = "0000000000"):
    #get user info from stablehorde
    #return user info if successful, empty dict if not
    """ User Info Format:
    {
    "username": "string",
    "id": 0,
    "kudos": 0,
    "evaluating_kudos": 0,
    "concurrency": 0,
    "worker_invited": 0,
    "moderator": false,
    "kudos_details": {
        "accumulated": 0,
        "gifted": 0,
        "admin": 0,
        "received": 0,
        "recurring": 0,
        "awarded": 0
    },
    "worker_count": 0,
    "worker_ids": [
        "string"
    ],
    "monthly_kudos": {
        "amount": 0,
        "last_received": "2023-04-18T00:03:35.937Z"
    },
    "trusted": false,
    "flagged": false,
    "suspicious": 0,
    "pseudonymous": false,
    "contact": "email@example.com",
    "account_age": 60,
    "usage": {
        "megapixelsteps": 0,
        "requests": 0
    },
    "contributions": {
        "megapixelsteps": 0,
        "fulfillments": 0
    },
    "records": {
        "usage": {
        "megapixelsteps": 0,
        "tokens": 0
        },
        "contribution": {
        "megapixelsteps": 0,
        "tokens": 0
        },
        "fulfillment": {
        "image": 0,
        "text": 0,
        "interrogation": 0
        },
        "request": {
        "image": 0,
        "text": 0,
        "interrogation": 0
        }
    }
    }
    """
    url = API_ROOT + "find_user"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "apikey": apikey, "Client-Agent": CLIENT_AGENT}
    try:
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        userInfo = json.loads(data)
    except urllib.error.URLError as e:
        utility.errorMessage("find_user url error", e.reason)
        userInfo = {}
    except:
        utility.errorMessage("Error", "Something went wrong while trying to get user info.")
        userInfo = {}

    return userInfo


def generate_async(data, apikey = "0000000000"):
    #generate image from stablehorde
    #return job id if successful, issue message if not
    """Response Format:
    Success:
    {
    "id": "string",
    "message": "string"
    }
    Failure: 
    {
    "message": "string"
    }
    """

    data = json.dumps(data).encode("utf-8") #format for sending request
    url = API_ROOT + "generate/async"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "apikey": apikey, "Client-Agent": CLIENT_AGENT}
    try:
        request = urllib.request.Request(url=url, data=data, headers=headers)
        response = urllib.request.urlopen(request)
        status = response.read()
        jobInfo = json.loads(status)
    except urllib.error.URLError as e:
        utility.errorMessage("generate_async url error", e.reason)
        jobInfo = {}
    except:
        utility.errorMessage("Error", "Something went wrong while trying to request an image.")
        jobInfo = {}
        
    return jobInfo
    

