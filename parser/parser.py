import os
import requests
import time
from typing import Optional
from dao import TMDB_DAO

class Parser:
  def __init__(self, db: TMDB_DAO):
    self.api_key = os.getenv("TMDB_API_KEY")
    if not self.api_key:
      raise EnvironmentError("TMDB_API_KEY environment variable is not set")
    self.db = db

  def fetchInformation(self, url) -> Optional[dict]:
    params = {
      "api_key": self.api_key,
      "language": "en-US",
      "append_to_response": "credits,videos,images,keywords",
    }

    try:
      response = requests.get(url, headers={"accept": "application/json"}, params=params)
      response.raise_for_status()
      return response.json()

    except requests.exceptions.HTTPError as e:
      if e.response is not None and e.response.status_code == 429:
        retry_after = int(e.response.headers.get("Retry-After", 5))
        print(f"Rate limited (429). Sleeping for {retry_after}s before retrying...")
        time.sleep(retry_after)
        return self.fetchInformation(url)

      print(f"HTTP error fetching TMDB data: {e}")
      return None

    except requests.exceptions.RequestException as e:
      print(f"Request failed: {e}")
      return None

  def fetchMediaInformation(self, tmdbId: str, mediaType: str) -> Optional[dict]:
    url = f"https://api.themoviedb.org/3/{mediaType}/{tmdbId}"
    return self.fetchInformation(url)

  def fetchPersonInformation(self, tmdbId: str) -> Optional[dict]:
    url = f"https://api.themoviedb.org/3/person/{tmdbId}"
    return self.fetchInformation(url)

  def parseMediaDict(self, mediaDict: dict, mediaType: str) -> None:
    try:
      collection = mediaDict.get("belongs_to_collection")
      if collection:
        self.db.upsert_collection(collection)
      self.db.upsert_media(mediaDict, mediaType)
      media_id = mediaDict["id"]
      genres = mediaDict.get("genres", [])
      self.db.upsert_genres(genres)
      self.db.link_media_genres(media_id, genres)
      companies = mediaDict.get("production_companies", [])
      self.db.upsert_production_companies(companies)
      self.db.link_media_production_companies(media_id, companies)
      countries = mediaDict.get("production_countries", [])
      self.db.upsert_production_countries(countries)
      self.db.link_media_production_countries(media_id, countries)
      languages = mediaDict.get("spoken_languages", [])
      self.db.upsert_spoken_languages(languages)
      self.db.link_media_spoken_languages(media_id, languages)
      keywords = mediaDict.get("keywords", {})
      keyword_list = keywords.get("keywords", keywords.get("results", []))
      self.db.upsert_keywords(keyword_list)
      self.db.link_media_keywords(media_id, keyword_list)
      credits = mediaDict.get("credits", {})
      for person in credits.get("cast", []) + credits.get("crew", []):
        self.db.upsert_person(person)
      self.db.upsert_cast(media_id, credits.get("cast", []))
      self.db.upsert_crew(media_id, credits.get("crew", []))
      self.db.insert_images(media_id, mediaDict.get("images", {}))
      self.db.insert_videos(media_id, mediaDict.get("videos", {}).get("results", []))
      if mediaType == "tv":
        seasons = mediaDict.get("seasons", [])
        self.db.upsert_seasons(media_id, seasons)
        for season in seasons:
          self.db.upsert_episodes(media_id, season["id"], season.get("episodes", []))
      self.db._commit()
    except Exception as e:
      self.db._rollback()
      raise e

  def parse(self, tmdbId: str, mediaType: str) -> None:
    if(mediaType == "person"):
      mediaDict = self.fetchPersonInformation(tmdbId)
    else:
      mediaDict = self.fetchMediaInformation(tmdbId, mediaType)
    print(tmdbId)
    if mediaDict:
      self.parseMediaDict(mediaDict, mediaType)
