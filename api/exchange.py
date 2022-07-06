import requests


def get_price(token: str, fiat:str):
    url = "https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies={fiat}".format(token=token, fiat=fiat)

    headers = {'accept': 'application/json'}

    return requests.get(url, headers=headers).json()[token][fiat]

