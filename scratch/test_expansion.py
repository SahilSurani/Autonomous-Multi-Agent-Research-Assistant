import requests

def test_crossref(query):
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": 3}
    headers = {"User-Agent": "PrismResearchAssistant/1.0 (mailto:support@prism-ai.org)"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"\n--- Crossref results for '{query}' ---")
            items = response.json().get("message", {}).get("items", [])
            for item in items:
                title = item.get("title", ["No Title"])[0]
                print(f" - Title: {title}")
        else:
            print(f"Crossref error: {response.status_code}")
    except Exception as e:
        print(f"Crossref failed: {e}")

if __name__ == "__main__":
    test_crossref("GOC chemistry definition")
    test_crossref("General Organic Chemistry definition")
