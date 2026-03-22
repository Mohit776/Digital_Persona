import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LINKD_API_KEY")
BASE_URL = "https://linkdapi.com"

def _make_request(endpoint, params):
    if not API_KEY:
        raise Exception("LINKD_API_KEY missing in .env")
    
    headers = {
        "X-linkdapi-apikey": API_KEY
    }
    
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 404:
        raise Exception("Profile not found or is private.")
    elif response.status_code == 429:
        raise Exception("Rate limit exceeded for the API. Please try again later.")
    elif response.status_code >= 400:
        raise Exception(f"API Error ({response.status_code}): {response.text}")
    
    try:
        return response.json()
    except:
        raise Exception(f"Invalid JSON response: {response.text[:100]}")

def fetch_profile(profile_url):
    if not profile_url or "/in/" not in profile_url:
        raise ValueError("Invalid LinkedIn URL format. Expected format: 'linkedin.com/in/username'.")
        
    # Step 1: Get URN from username
    username = profile_url.split("/in/")[-1].strip("/")
    if "?" in username:
        username = username.split("?")[0]
    username = username.strip("/")
        
    if not username:
        raise ValueError("Could not extract username from the provided URL.")
        
    urn_data = _make_request("/api/v1/profile/username-to-urn", {"username": username})
    
    if not urn_data.get("success") or not urn_data.get("data"):
        raise Exception(f"Could not find URN for username: {username}")
        
    urn = urn_data["data"]["urn"]
    
    # Step 2: Get Full Profile
    profile_data = _make_request("/api/v1/profile/full", {"username": username, "urn": urn})
    
    # Step 3: Get Posts
    posts_data = _make_request("/api/v1/posts/all", {"urn": urn, "start": 0})
    
    return {
        "profile": profile_data.get("data", {}),
        "posts": posts_data.get("data", []),
        "username": username,
        "urn": urn
    }