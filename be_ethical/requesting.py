import requests


def validateStatusCode(status_code : int, valid_range : list[int,int] = [199,300],silence : bool = True) -> bool:
    if status_code > valid_range[0] and status_code < valid_range[-1]:
        return True
    if not silence:
        print(f'Invalid status_code: {status_code}')
    return False

def sendRequest(link : str, silence : bool = True) -> requests.Response|None:
    try:
        response = requests.get(url=link)
    except Exception as e:
        if not silence:
            print(f'Trouble sending request for "{link}":\n--> {e.__class__.__name__}: {str(e)}')
        return None
    else:
        return response
