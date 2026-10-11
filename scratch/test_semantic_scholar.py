import requests
import os
import json

def test_semantic_scholar():
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    query = "Quantum Machine Learning Algorithms"
    params = {
        "query": query,
        "limit": 5,
        "fields": "title,authors,abstract,year,citationCount,venue,url,externalIds"
    }
    headers = {}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key.strip()
    
    print(f"Using API Key: {api_key is not None}")
    response = requests.get(url, params=params, headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        for p in data.get("data", []):
            print(f"Title: {p.get('title')}")
            print(f"Venue: {p.get('venue')}")
            print(f"URL: {p.get('url')}")
            print(f"ExternalIds: {p.get('externalIds')}")
            print("-" * 40)
    else:
        print(response.text)

if __name__ == "__main__":
    test_semantic_scholar()
