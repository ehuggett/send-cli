import sendclient.common
import requests

def api_password(service, fileId , ownerToken, newAuthKey):
    '''
        changes the authKey required to download a file hosted on a send server
    '''

    service += 'api/password/%s' % fileId
    auth = sendclient.common.unpadded_urlsafe_b64encode(newAuthKey)
    r = requests.post(service, json={'owner_token': ownerToken, 'auth': auth})
    r.raise_for_status()

    if r.text == 'OK':
        return True
    return False

def set_password(url, ownerToken, password):
    '''
        set or change the password required to download a file hosted on a send server.
    '''
    
    service, fileId, key = sendclient.common.splitkeyurl(url)
    rawKey = sendclient.common.unpadded_urlsafe_b64decode(key)
    keys = sendclient.common.secretKeys(rawKey, password, url)
    
    return api_password(service, fileId, ownerToken, keys.newAuthKey)