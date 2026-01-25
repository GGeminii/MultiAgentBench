import requests
from bs4 import BeautifulSoup

def test_init() -> None:
    response = requests.get("https://arxiv.org/html/2406.00239v1", timeout=60)
    if response.status_code == 200:
        print(response.text)
        res = BeautifulSoup(response.text, "lxml")
        print(res)
    else:
        print(response)