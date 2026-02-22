import asyncio
import sys
import io
import aiohttp
from bs4 import BeautifulSoup

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_search():
    query = "test query"
    print(f"Searching web for: {query}")
    
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print("Sending request...")
            async with session.post(url, data=data, headers=headers) as response:
                print(f"Status: {response.status}")
                if response.status != 200:
                    print(f"Failed: {response.status}")
                    return
                print("Reading text...")
                html = await response.text()
                print(f"Read {len(html)} bytes")
                
                print("Parsing HTML...")
                soup = BeautifulSoup(html, 'html.parser')
                results = soup.find_all('div', class_='result')
                print(f"Found {len(results)} results")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
