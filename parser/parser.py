import os
import time
from fetcher import fetchMediaInformation, fetchPersonInformation
from dao import TMDB_DAO

class Parser:
  def __init__(self, db: TMDB_DAO):
    self.api_key = os.getenv("TMDB_API_KEY")
    if not self.api_key:
      raise EnvironmentError("TMDB_API_KEY environment variable is not set")
    self.db = db

  def parseMediaDict(self, mediaDict: dict, mediaType: str) -> None:
    try:
      collection = mediaDict.get("belongs_to_collection")
      if collection:
        self.db.upsert_collection(collection)

      self.db.upsert_media(mediaDict, mediaType)
      media_id = mediaDict["id"]

      genres = mediaDict.get("genres", [])
      self.db.upsert_genres(genres)
      self.db.link_media_genres(media_id, mediaType, genres)

      companies = mediaDict.get("production_companies", [])
      self.db.upsert_production_companies(companies)
      self.db.link_media_production_companies(media_id, mediaType, companies)

      countries = mediaDict.get("production_countries", [])
      self.db.upsert_production_countries(countries)
      self.db.link_media_production_countries(media_id, mediaType, countries)

      languages = mediaDict.get("spoken_languages", [])
      self.db.upsert_spoken_languages(languages)
      self.db.link_media_spoken_languages(media_id, mediaType,  languages)

      keywords = mediaDict.get("keywords", {})
      keyword_list = keywords.get("keywords", keywords.get("results", []))
      self.db.upsert_keywords(keyword_list)
      self.db.link_media_keywords(media_id, mediaType, keyword_list)

      credits = mediaDict.get("credits", {})
      for person in credits.get("cast", []) + credits.get("crew", []):
        self.db.upsert_person(person)
      self.db.upsert_cast(media_id, mediaType, credits.get("cast", []))
      self.db.upsert_crew(media_id, mediaType, credits.get("crew", []))

      self.db.insert_images(media_id, mediaType, mediaDict.get("images", {}))
      self.db.insert_videos(media_id, mediaType, mediaDict.get("videos", {}).get("results", []))
      
      if mediaType == "tv":
        seasons = mediaDict.get("seasons", [])
        self.db.upsert_seasons(media_id, mediaType, seasons)
        for season in seasons:
          self.db.upsert_episodes(media_id, mediaType, season["id"], season.get("episodes", []))
      self.db._commit()
    except Exception as e:
      self.db._rollback()
      raise e

  def parsePersonDict(self, personDict) -> None:
    self.db.upsert_person(personDict)

  def fetchAndStore(self, tmdbId: str, mediaType: str) -> None:
    start = time.time()
    print(f"Fetching Info for: {tmdbId} ({mediaType})")
    if(mediaType == "person"):
      personDict = fetchPersonInformation(self.api_key, tmdbId)
      if(personDict):
        print("Parsing info into db ... ")
        self.parsePersonDict(personDict)
    else:
      mediaDict = fetchMediaInformation(self.api_key, tmdbId, mediaType)
      if mediaDict:
        print("Parsing info into db ... ")
        self.parseMediaDict(mediaDict, mediaType)

    elapsed = time.time() - start
    print(f"Done processing {tmdbId} ({mediaType}) in {elapsed:.2f}s\n")
