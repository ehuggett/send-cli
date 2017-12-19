import requests

def api_delete(service, file_id, owner_token):
    """Delete a file already uploaded to Send"""
    service += 'api/delete/%s' % file_id
    r = requests.post(service, json={'owner_token': owner_token, 'delete_token': owner_token})
    r.raise_for_status()

    if r.text == 'OK':
        return True
    return False
