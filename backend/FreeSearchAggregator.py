import requests
from ddgs import DDGS
from typing import List, Dict
import json


class FreeSearchAggregator:
    """Aggregate results from multiple FREE search providers"""
    
    def search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict]:
        """DuckDuckGo - Completely free, no API key"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return self._normalize_duckduckgo(results)
        except Exception as e:
            print(f"DuckDuckGo failed: {e}")
            return []
    
    # API Key not generated - Do not use this for now
    def search_brave(self, query: str, max_results: int = 10) -> List[Dict]:
        """Brave Search - Free tier: 2000 queries/month"""
        try:
            # Sign up for free API key at https://brave.com/search/api/
            api_key = os.getenv("BRAVE_API_KEY")  # Optional, free tier available
            if not api_key:
                return []
                
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {"X-Subscription-Token": api_key}
            params = {"q": query, "count": max_results}
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            return self._normalize_brave(data.get("web", {}).get("results", []))
        except Exception as e:
            print(f"Brave Search failed: {e}")
            return []
    
    def search_wikipedia(self, query: str, max_results: int = 5) -> List[Dict]:
        """Wikipedia API - Completely free"""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": query,
                "limit": max_results,
                "format": "json"
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            results = []
            titles = data[1]
            descriptions = data[2]
            urls = data[3]
            
            for i in range(len(titles)):
                results.append({
                    "title": titles[i],
                    "snippet": descriptions[i],
                    "url": urls[i],
                    "domain": "wikipedia.org",
                    "source": "wikipedia"
                })
            return results
        except Exception as e:
            print(f"Wikipedia failed: {e}")
            return []
    
    def search_reddit(self, query: str, max_results: int = 5) -> List[Dict]:
        """Reddit API - Free, no auth needed for basic search"""
        try:
            url = "https://www.reddit.com/search.json"
            headers = {"User-Agent": "Mozilla/5.0"}
            params = {"q": query, "limit": max_results}
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            results = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                results.append({
                    "title": post_data.get("title", ""),
                    "snippet": post_data.get("selftext", "")[:300],
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "domain": "reddit.com",
                    "source": "reddit",
                    "score": post_data.get("score", 0)
                })
            return results
        except Exception as e:
            print(f"Reddit search failed: {e}")
            return []
    
    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict]:
        """arXiv API - Free academic papers"""
        try:
            import urllib.parse
            url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={max_results}"
            
            response = requests.get(url)
            
            # Parse XML response
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.content)
            
            results = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                link = entry.find('{http://www.w3.org/2005/Atom}id').text
                
                results.append({
                    "title": title.strip(),
                    "snippet": summary.strip()[:300],
                    "url": link,
                    "domain": "arxiv.org",
                    "source": "arxiv"
                })
            return results
        except Exception as e:
            print(f"arXiv search failed: {e}")
            return []
    
    def search_github(self, query: str, max_results: int = 5) -> List[Dict]:
        """GitHub API - Free, no auth for basic search"""
        try:
            url = "https://api.github.com/search/repositories"
            headers = {"Accept": "application/vnd.github.v3+json"}
            params = {"q": query, "per_page": max_results, "sort": "stars"}
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            results = []
            for repo in data.get("items", []):
                results.append({
                    "title": repo.get("full_name", ""),
                    "snippet": repo.get("description", "")[:300],
                    "url": repo.get("html_url", ""),
                    "domain": "github.com",
                    "source": "github",
                    "stars": repo.get("stargazers_count", 0)
                })
            return results
        except Exception as e:
            print(f"GitHub search failed: {e}")
            return []
    
    def aggregate_search(self, query: str, sources: List[str] = None) -> List[Dict]:
        """
        Aggregate results from multiple free sources
        sources: list of sources to use, or None for all
        """
        if sources is None:
            sources = ["duckduckgo", "wikipedia", "reddit"]
        
        all_results = []
        
        if "duckduckgo" in sources:
            all_results.extend(self.search_duckduckgo(query))
        
        if "brave" in sources:
            all_results.extend(self.search_brave(query))
        
        if "wikipedia" in sources:
            all_results.extend(self.search_wikipedia(query))
        
        if "reddit" in sources:
            all_results.extend(self.search_reddit(query))
        
        if "arxiv" in sources:
            all_results.extend(self.search_arxiv(query))
        
        if "github" in sources:
            all_results.extend(self.search_github(query))
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _normalize_duckduckgo(self, results: List) -> List[Dict]:
        """Normalize DuckDuckGo results"""
        normalized = []
        for i, result in enumerate(results):
            normalized.append({
                "title": result.get("title", ""),
                "snippet": result.get("body", ""),
                "url": result.get("href", ""),
                "domain": self._extract_domain(result.get("href", "")),
                "source": "duckduckgo",
                "rank": i + 1
            })
        return normalized
    
    def _normalize_brave(self, results: List) -> List[Dict]:
        """Normalize Brave Search results"""
        normalized = []
        for i, result in enumerate(results):
            normalized.append({
                "title": result.get("title", ""),
                "snippet": result.get("description", ""),
                "url": result.get("url", ""),
                "domain": self._extract_domain(result.get("url", "")),
                "source": "brave",
                "rank": i + 1
            })
        return normalized
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        try:
            return urlparse(url).netloc
        except:
            return ""
