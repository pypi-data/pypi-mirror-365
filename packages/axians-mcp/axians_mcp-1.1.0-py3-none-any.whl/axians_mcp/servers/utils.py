import requests
from bs4 import BeautifulSoup

def fetch_iceland_page(label: str, url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')


    for tag in soup(["style", "script", "table", "noscript", "iframe", "form", "header", "footer","span"]):
        tag.decompose()  # Supprime complètement la balise

    title = soup.find("h1").get_text(strip=True)
    paragraphs = [
        p.get_text(strip=True)
        for p in soup.select("p")
        if p.get_text(strip=True)  # ignore les p vides
    ]

    return {
        "title": title,
        "summary": paragraphs,
        "topic": label
    }