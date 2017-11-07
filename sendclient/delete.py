import requests

def api_delete(service, file_id, delete_token):
    """Delete a file already uploaded to Send"""
    service += 'api/delete/%s' % file_id
    r = requests.post(service, json={'delete_token': delete_token})
    r.raise_for_status()

    if r.text == 'OK':
        return True
    return False
