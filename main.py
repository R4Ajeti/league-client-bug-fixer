import requests
import urllib3
import base64
import json
import os

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def encodeBase64(inputString):
    # Convert the input string to bytes
    inputBytes = inputString.encode('utf-8')
    # Encode the bytes to base64
    base64Bytes = base64.b64encode(inputBytes)
    # Convert the base64 bytes back to a string
    base64String = base64Bytes.decode('utf-8')
    return base64String

def getSummonerId(summonerName, tagLine, apiKey):
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summonerName}/{tagLine}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.6",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": apiKey
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise Exception(f"Failed to get summoner id for {summonerName}#{tagLine} - {response.status_code}")
    return response.json()["puuid"]

def getSummonerData(summonerId, region, apiKey):
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summonerId}"
    headers = {
        "X-Riot-Token": apiKey
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise Exception(f"Failed to get summoner data for {summonerId} - {response.status_code}")
    return response.json()

def getLockfileData():
    data = {}
    try:
        lockfilePath = os.path.join(os.getenv('LOCALAPPDATA'), 'Riot Games', 'League of Legends', 'lockfile')
        with open(lockfilePath, 'r') as file:
            data = file.read().split(':')
    except Exception as e:
        data = os.getenv('FULL_CLIENT_DETAIL').split(':')
    return {
            'name': data[0],
            'pid': data[1],
            'port': data[2],
            'authToken': data[3],
            'protocol': data[4]
        }

def getLcuRunePages(port, base64AuthToken):
    url = f'https://127.0.0.1:{port}/lol-perks/v1/pages'
    headers = {
        'Authorization': f'Basic {base64AuthToken}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=False)
    if response.ok:
        runePages = response.json()
        return runePages
    else:
        raise Exception(f"Failed to fetch rune pages - {response.status_code}")
    
def deleteAllRunePage(port, base64AuthToken):
    url = f'https://127.0.0.1:{port}/lol-perks/v1/pages'
    headers = {
        'Authorization': f'Basic {base64AuthToken}',
        'Accept': 'application/json'
    }

    response = requests.delete(url, headers=headers, verify=False)
    if response.ok:
        print(f"Successfully deleted all rune pages {response.status_code}.")
    else:
        print(f"Failed to delete all rune page - {response.status_code}")
    
def isLcuServerRunning(port, base64AuthToken):
    url = f'https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase'
    headers = {
        'Authorization': f'Basic {base64AuthToken}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        print("Response status code:", response.status_code)
        print("Response content:", response.content)

        if response.ok:
            print("LCU server is running.")
            return True
        else:
            print(f"LCU server returned status code {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to LCU server: {e}")
        return False

# Replace with your details
summonerName = "rinor4ever"
tagLine = "EUW"
region = "euw1"
apiKey = os.environ.get("RIOT_API_KEY", None)

summonerId = getSummonerId(summonerName, tagLine, apiKey)
print('summonerId', summonerId)

summonerData = getSummonerData(summonerId, region, apiKey)
print('summonerData', summonerData)

# Fetch lockfile data
lockfileData = getLockfileData()


stringAuth = f"riot:{lockfileData['authToken']}"
base64AuthToken = encodeBase64(stringAuth)

# Check if LCU server is running
isLcuServerRunning(lockfileData['port'], base64AuthToken)

# Fetch rune pages
runePages = getLcuRunePages(lockfileData['port'], base64AuthToken)
# print(json.dumps(runePages, indent=4))
# print(runePages)
print(len(runePages))
filteredRunPages = [item["id"] for item in runePages if item["isDeletable"]]

print(len(filteredRunPages), filteredRunPages)

# deleteAllRunePage(lockfileData['port'], base64AuthToken)