import requests
import xml.etree.ElementTree as ET
import time

def test_arxiv_query(query, use_user_agent=True):
    url = "https://export.arxiv.org/api/query"
    words = [w.strip() for w in query.split() if w.strip()]
    arxiv_query = " AND ".join([f"all:{w}" for w in words])
    
    params = {
        "search_query": arxiv_query,
        "max_results": 5,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    headers = {}
    if use_user_agent:
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutonomousResearchAssistant/1.0"
        
    print(f"Testing query: '{arxiv_query}' with User-Agent: {use_user_agent}")
    
    try:
        t0 = time.time()
        response = requests.get(url, params=params, headers=headers, timeout=10)
        t1 = time.time()
        print(f"Status Code: {response.status_code}, Time taken: {t1 - t0:.2f}s")
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', ns)
            print(f"Found {len(entries)} entries")
            for entry in entries[:2]:
                title = entry.find('atom:title', ns).text.strip()
                print(f" - Title: {title}")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_arxiv_query("Quantum Machine Learning Algorithms", use_user_agent=True)
    time.sleep(3)
    test_arxiv_query("Quantum Machine Learning Algorithms", use_user_agent=False)
