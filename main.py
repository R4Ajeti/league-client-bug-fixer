import requests
import json
import os

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
    try:
        lockfilePath = os.path.join(os.getenv('LOCALAPPDATA'), 'Riot Games', 'League of Legends', 'lockfile')
        with open(lockfilePath, 'r') as file:
            data = file.read().split(':')
        return {
            'port': data[2],
            'authToken': data[3]
        }
    except Exception as e:
        data = os.getenv('FULL_CLIENT_DETAIL').split(':')
        return {
            'port': data[2],
            'authToken': data[3]
        }

def getLcuRunePages(port, authToken):
    url = f'https://127.0.0.1:{port}/lol-perks/v1/pages'
    headers = {
        'Authorization': f'Basic {authToken}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=False)
    if response.ok:
        runePages = response.json()
        return runePages
    else:
        raise Exception(f"Failed to fetch rune pages - {response.status_code}")

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

# Fetch rune pages
runePages = getLcuRunePages(lockfileData['port'], lockfileData['authToken'])
print(json.dumps(runePages, indent=4))