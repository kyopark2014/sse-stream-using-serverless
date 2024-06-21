import boto3
import os
import time
import re
import base64
import boto3
import uuid
import json
import redis
import traceback

# Redis
redisAddress = os.environ.get('redisAddress')
print('redisAddress: ',redisAddress)
redisPort = os.environ.get('redisPort')
print('redisPort: ',redisPort)

def initiate_redis():
    try: 
        client = redis.Redis(host=redisAddress, port=redisPort, db=0, charset="utf-8", decode_responses=True)    
        print('Redis was connected')
        
    except Exception:
        err_msg = traceback.format_exc()
        print('error message: ', err_msg)                    
        raise Exception ("Not able to request to redis")        
    
    return client
    
redis_client = initiate_redis()

"""
def subscribe_redis(channel):    
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    print('successfully subscribed for channel: ', channel)    
            
    for message in pubsub.listen():
        print('message: ', message)
                
        if message['data'] != 1:            
            msg = message['data'].encode('utf-8').decode('unicode_escape')
            # msg = msg[1:len(msg)-1]
            print('msg: ', msg)                        
            #deliveryVoiceMessage(msg)

subscribe_redis('a1234')
"""

def lambda_handler(event, context):
    print('event: ', json.dumps(event))
    
    eventType = event['type']
    userId = event['user-id']
    # msg = event
    
    if eventType == 'init':
        sessionId = event['session-id']
        channel = f"{sessionId}"        
        msg = {
            'type': eventType,
            'session-id': sessionId,
            'user-id': userId
        }
    else:
        channel = f"{userId}"   
        msg = event
        
    print('channel: ', channel)
    print('msg: ', msg)
    
    try: 
        redis_client.publish(channel=channel, message=json.dumps(msg))
        print('successfully published: ', json.dumps(msg))
    
    except Exception:
        err_msg = traceback.format_exc()
        print('error message: ', err_msg)                    
        raise Exception ("Not able to request to redis")
        
    msg = "success"
    
    return {
        "isBase64Encoded": False,
        'statusCode': 200,
        'body': json.dumps({ 
            "channel": channel
        })
    }