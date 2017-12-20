import requests

def api_params(service, file_id, owner_token, download_limit):
    """Change the download limit for a file hosted on a Send Server"""
    service += 'api/params/%s' % file_id
    r = requests.post(service, json={'owner_token': owner_token, 'dlimit': download_limit})
    r.raise_for_status()

    if r.text == 'OK':
        return True
    return False
