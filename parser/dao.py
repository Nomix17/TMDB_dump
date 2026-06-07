import os
import psycopg2
from psycopg2.extras import execute_values
from collections import defaultdict

class TMDB_DAO:
  def __init__(self):
    self.connection = psycopg2.connect(
      dbname=os.getenv("DB_NAME"),
      user=os.getenv("DB_USER"),
      password=os.getenv("DB_PASSWORD"),
      host=os.getenv("DB_HOST", "localhost"),
      port=os.getenv("DB_PORT", 5432),
    )
    self.cursor = self.connection.cursor()

  def _commit(self):
    self.connection.commit()

  def _rollback(self):
    self.connection.rollback()

  def close(self):
    self.cursor.close()
    self.connection.close()

  def upsert_collection(self, info: dict):
    sanitized_info = {k: (None if v == "" else v) for k, v in info.items()}
    safe_data = defaultdict(lambda: None, sanitized_info)
    self.cursor.execute(
      """
      INSERT INTO collections (id, name, overview, poster_path, backdrop_path)
      VALUES (%(id)s, %(name)s, %(overview)s, %(poster_path)s, %(backdrop_path)s)
      ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        overview = EXCLUDED.overview,
        poster_path = EXCLUDED.poster_path,
        backdrop_path = EXCLUDED.backdrop_path
      """,
      safe_data,
    )

  def upsert_media(self, info: dict, media_type: str):
    sanitized_info = {k: (None if v == "" else v) for k, v in info.items()}
    full_data = {**sanitized_info, "media_type": media_type}
    safe_data = defaultdict(lambda: None, full_data)
    self.cursor.execute(
      """
      INSERT INTO media (
        id, media_type, title, original_title, original_language,
        overview, tagline, status, homepage, release_date,
        runtime, budget, revenue, popularity, vote_average,
        vote_count, adult, video, poster_path, backdrop_path,
        imdb_id, origin_country, collection_id
      ) VALUES (
        %(id)s, %(media_type)s, %(title)s, %(original_title)s, %(original_language)s,
        %(overview)s, %(tagline)s, %(status)s, %(homepage)s, %(release_date)s,
        %(runtime)s, %(budget)s, %(revenue)s, %(popularity)s, %(vote_average)s,
        %(vote_count)s, %(adult)s, %(video)s, %(poster_path)s, %(backdrop_path)s,
        %(imdb_id)s, %(origin_country)s, %(collection_id)s
      )
      ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        original_title = EXCLUDED.original_title,
        original_language = EXCLUDED.original_language,
        overview = EXCLUDED.overview,
        tagline = EXCLUDED.tagline,
        status = EXCLUDED.status,
        homepage = EXCLUDED.homepage,
        release_date = EXCLUDED.release_date,
        runtime = EXCLUDED.runtime,
        budget = EXCLUDED.budget,
        revenue = EXCLUDED.revenue,
        popularity = EXCLUDED.popularity,
        vote_average = EXCLUDED.vote_average,
        vote_count = EXCLUDED.vote_count,
        adult = EXCLUDED.adult,
        video = EXCLUDED.video,
        poster_path = EXCLUDED.poster_path,
        backdrop_path = EXCLUDED.backdrop_path,
        imdb_id = EXCLUDED.imdb_id,
        origin_country = EXCLUDED.origin_country,
        collection_id = EXCLUDED.collection_id
      """,
      safe_data,
    )

  def upsert_genres(self, genres: list[dict]):
    if not genres:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO genres (id, name) VALUES %s
      ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
      """,
      [(g["id"], g["name"]) for g in genres],
    )

  def upsert_production_companies(self, companies: list[dict]):
    if not companies:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO production_companies (id, name, logo_path, origin_country)
      VALUES %s
      ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        logo_path = EXCLUDED.logo_path,
        origin_country = EXCLUDED.origin_country
      """,
      [(c["id"], c["name"], c.get("logo_path"), c.get("origin_country")) for c in companies],
    )

  def upsert_production_countries(self, countries: list[dict]):
    if not countries:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO production_countries (iso_3166_1, name) VALUES %s
      ON CONFLICT (iso_3166_1) DO UPDATE SET name = EXCLUDED.name
      """,
      [(c["iso_3166_1"], c["name"]) for c in countries],
    )

  def upsert_spoken_languages(self, languages: list[dict]):
    if not languages:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO spoken_languages (iso_639_1, name, english_name) VALUES %s
      ON CONFLICT (iso_639_1) DO UPDATE SET
        name = EXCLUDED.name,
        english_name = EXCLUDED.english_name
      """,
      [(l["iso_639_1"], l.get("name"), l.get("english_name")) for l in languages],
    )

  def upsert_keywords(self, keywords: list[dict]):
    if not keywords:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO keywords (id, name) VALUES %s
      ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
      """,
      [(k["id"], k["name"]) for k in keywords],
    )

  def link_media_genres(self, media_id: int, genres: list[dict]):
    if not genres:
      return
    execute_values(
      self.cursor,
      "INSERT INTO media_genres (media_id, genre_id) VALUES %s ON CONFLICT DO NOTHING",
      [(media_id, g["id"]) for g in genres],
    )

  def link_media_production_companies(self, media_id: int, companies: list[dict]):
    if not companies:
      return
    execute_values(
      self.cursor,
      "INSERT INTO media_production_companies (media_id, company_id) VALUES %s ON CONFLICT DO NOTHING",
      [(media_id, c["id"]) for c in companies],
    )

  def link_media_production_countries(self, media_id: int, countries: list[dict]):
    if not countries:
      return
    execute_values(
      self.cursor,
      "INSERT INTO media_production_countries (media_id, country_iso) VALUES %s ON CONFLICT DO NOTHING",
      [(media_id, c["iso_3166_1"]) for c in countries],
    )

  def link_media_spoken_languages(self, media_id: int, languages: list[dict]):
    if not languages:
      return
    execute_values(
      self.cursor,
      "INSERT INTO media_spoken_languages (media_id, language_iso) VALUES %s ON CONFLICT DO NOTHING",
      [(media_id, l["iso_639_1"]) for l in languages],
    )

  def link_media_keywords(self, media_id: int, keywords: list[dict]):
    if not keywords:
      return
    execute_values(
      self.cursor,
      "INSERT INTO media_keywords (media_id, keyword_id) VALUES %s ON CONFLICT DO NOTHING",
      [(media_id, k["id"]) for k in keywords],
    )

  def upsert_person(self, info: dict):
    sanitized_info = {k: (None if v == "" else v) for k, v in info.items()}
    safe_data = defaultdict(lambda: None, sanitized_info)
    self.cursor.execute(
      """
      INSERT INTO persons (
        id, name, also_known_as, biography, birthday, deathday,
        gender, place_of_birth, popularity, profile_path, imdb_id, homepage
      ) VALUES (
        %(id)s, %(name)s, %(also_known_as)s, %(biography)s, %(birthday)s, %(deathday)s,
        %(gender)s, %(place_of_birth)s, %(popularity)s, %(profile_path)s, %(imdb_id)s, %(homepage)s
      )
      ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        also_known_as = EXCLUDED.also_known_as,
        biography = EXCLUDED.biography,
        birthday = EXCLUDED.birthday,
        deathday = EXCLUDED.deathday,
        gender = EXCLUDED.gender,
        place_of_birth = EXCLUDED.place_of_birth,
        popularity = EXCLUDED.popularity,
        profile_path = EXCLUDED.profile_path,
        imdb_id = EXCLUDED.imdb_id,
        homepage = EXCLUDED.homepage
      """,
      safe_data,
    )

  def upsert_cast(self, media_id: int, cast: list[dict]):
    if not cast:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO media_cast (media_id, person_id, character, "order", credit_id)
      VALUES %s ON CONFLICT DO NOTHING
      """,
      [(media_id, c["id"], c.get("character"), c.get("order"), c.get("credit_id")) for c in cast],
    )

  def upsert_crew(self, media_id: int, crew: list[dict]):
    if not crew:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO media_crew (media_id, person_id, job, department, credit_id)
      VALUES %s ON CONFLICT DO NOTHING
      """,
      [(media_id, c["id"], c.get("job"), c.get("department"), c.get("credit_id")) for c in crew],
    )

  def insert_images(self, media_id: int, images: dict):
    rows = []
    for img_type, key in [("poster", "posters"), ("backdrop", "backdrops"), ("still", "stills")]:
      for img in images.get(key, []):
        rows.append((
          media_id, img_type, img["file_path"],
          img.get("width") if img.get("width") != "" else None,
          img.get("height") if img.get("height") != "" else None,
          img.get("iso_639_1"),
          img.get("vote_average") if img.get("vote_average") != "" else None,
          img.get("vote_count") if img.get("vote_count") != "" else None,
        ))
    if not rows:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO images (media_id, type, file_path, width, height, language, vote_average, vote_count)
      VALUES %s ON CONFLICT DO NOTHING
      """,
      rows,
    )

  def insert_videos(self, media_id: int, videos: list[dict]):
    if not videos:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO videos (id, media_id, name, key, site, type, official, published_at, language)
      VALUES %s ON CONFLICT (id) DO NOTHING
      """,
      [
        (
          v["id"], media_id, v.get("name"), v["key"],
          v.get("site"), v.get("type"), v.get("official"),
          v.get("published_at") if v.get("published_at") != "" else None,
          v.get("iso_639_1"),
        )
        for v in videos
      ],
    )

  def upsert_seasons(self, media_id: int, seasons: list[dict]):
    if not seasons:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO seasons (id, media_id, season_number, name, overview, poster_path, air_date, episode_count)
      VALUES %s
      ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        overview = EXCLUDED.overview,
        poster_path = EXCLUDED.poster_path,
        air_date = EXCLUDED.air_date,
        episode_count = EXCLUDED.episode_count
      """,
      [
        (
          s["id"], media_id, s["season_number"], s.get("name"),
          s.get("overview"), s.get("poster_path"),
          s.get("air_date") if s.get("air_date") != "" else None,
          s.get("episode_count") if s.get("episode_count") != "" else None
        )
        for s in seasons
      ],
    )

  def upsert_episodes(self, media_id: int, season_id: int, episodes: list[dict]):
    if not episodes:
      return
    execute_values(
      self.cursor,
      """
      INSERT INTO episodes (id, season_id, media_id, episode_number, name, overview, still_path, air_date, runtime, vote_average, vote_count)
      VALUES %s
      ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        overview = EXCLUDED.overview,
        still_path = EXCLUDED.still_path,
        air_date = EXCLUDED.air_date,
        runtime = EXCLUDED.runtime,
        vote_average = EXCLUDED.vote_average,
        vote_count = EXCLUDED.vote_count
      """,
      [
        (
          e["id"], season_id, media_id, e["episode_number"],
          e.get("name"), e.get("overview"), e.get("still_path"),
          e.get("air_date") if e.get("air_date") != "" else None,
          e.get("runtime") if e.get("runtime") != "" else None,
          e.get("vote_average") if e.get("vote_average") != "" else None,
          e.get("vote_count") if e.get("vote_count") != "" else None,
        )
        for e in episodes
      ],
    )
