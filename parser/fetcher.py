import time
import requests
from datetime import datetime, timedelta
from typing import Optional

def fetchInformation(api_key: str | None, url: str) -> Optional[dict]:
  params = {
    "api_key": api_key,
    "language": "en-US",
    "append_to_response": "credits,videos,images,keywords",
  }
  while True:
    try:
      response = requests.get(url, headers={"accept": "application/json"}, params=params)
      response.raise_for_status()
      return response.json()
    except requests.exceptions.HTTPError as e:
      if e.response is not None and e.response.status_code == 429:
        retry_after = int(e.response.headers.get("Retry-After", 5))
        print(f"Rate limited. Sleeping {retry_after}s...")
        time.sleep(retry_after)
        continue
      print(f"HTTP error: {e}")
      return None
    except requests.exceptions.RequestException as e:
      print(f"Request failed: {e}")
      return None

def fetchMediaInformation(api_key: str | None, tmdbId: str, mediaType: str) -> Optional[dict]:
  url = f"https://api.themoviedb.org/3/{mediaType}/{tmdbId}"
  return fetchInformation(api_key, url)

def fetchPersonInformation(api_key: str | None, tmdbId: str) -> Optional[dict]:
  url = f"https://api.themoviedb.org/3/person/{tmdbId}"
  return fetchInformation(api_key, url)

