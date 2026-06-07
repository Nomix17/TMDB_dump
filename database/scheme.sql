CREATE TABLE collections (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  overview TEXT,
  poster_path TEXT,
  backdrop_path TEXT
);

CREATE TABLE media (
  id INTEGER,
  media_type TEXT NOT NULL CHECK (media_type IN ('movie', 'tv')),
  title TEXT NOT NULL,
  original_title TEXT,
  original_language TEXT,
  overview TEXT,
  tagline TEXT,
  status TEXT,
  homepage TEXT,
  release_date DATE,
  runtime INTEGER,
  budget BIGINT,
  revenue BIGINT,
  popularity NUMERIC(10, 4),
  vote_average NUMERIC(6, 3),
  vote_count INTEGER,
  adult BOOLEAN DEFAULT FALSE,
  video BOOLEAN DEFAULT FALSE,
  poster_path TEXT,
  backdrop_path TEXT,
  imdb_id TEXT,
  origin_country TEXT[],
  collection_id INTEGER REFERENCES collections (id) ON DELETE SET NULL
  PRIMARY KEY (id, media_type)
);

CREATE TABLE persons (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  also_known_as TEXT[],
  biography TEXT,
  birthday DATE,
  deathday DATE,
  gender INTEGER,
  place_of_birth TEXT,
  popularity NUMERIC(10, 4),
  profile_path TEXT,
  imdb_id TEXT,
  homepage TEXT
);

CREATE TABLE genres (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE production_companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  logo_path TEXT,
  origin_country TEXT
);

CREATE TABLE production_countries (
  iso_3166_1 TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE spoken_languages (
  iso_639_1 TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  english_name TEXT
);

CREATE TABLE keywords (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE media_genres (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  genre_id INTEGER REFERENCES genres (id) ON DELETE CASCADE,
  PRIMARY KEY (media_id, genre_id)
);

CREATE TABLE media_production_companies (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  company_id INTEGER REFERENCES production_companies (id) ON DELETE CASCADE,
  PRIMARY KEY (media_id, company_id)
);

CREATE TABLE media_production_countries (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  country_iso TEXT REFERENCES production_countries (iso_3166_1) ON DELETE CASCADE,
  PRIMARY KEY (media_id, country_iso)
);

CREATE TABLE media_spoken_languages (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  language_iso TEXT REFERENCES spoken_languages (iso_639_1) ON DELETE CASCADE,
  PRIMARY KEY (media_id, language_iso)
);

CREATE TABLE media_keywords (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  keyword_id INTEGER REFERENCES keywords (id) ON DELETE CASCADE,
  PRIMARY KEY (media_id, keyword_id)
);

CREATE TABLE media_cast (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  person_id INTEGER REFERENCES persons (id) ON DELETE CASCADE,
  character TEXT,
  "order" INTEGER,
  credit_id TEXT,
  PRIMARY KEY (media_id, person_id, credit_id)
);

CREATE TABLE media_crew (
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  person_id INTEGER REFERENCES persons (id) ON DELETE CASCADE,
  job TEXT,
  department TEXT,
  credit_id TEXT,
  PRIMARY KEY (media_id, person_id, credit_id)
);

CREATE TABLE images (
  id SERIAL PRIMARY KEY,
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  type TEXT CHECK (type IN ('poster', 'backdrop', 'still')),
  file_path TEXT NOT NULL,
  width INTEGER,
  height INTEGER,
  language TEXT,
  vote_average NUMERIC(6, 3),
  vote_count INTEGER
)
;
CREATE TABLE videos (
  id TEXT PRIMARY KEY,
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  name TEXT,
  key TEXT NOT NULL,
  site TEXT,
  type TEXT,
  official BOOLEAN DEFAULT FALSE,
  published_at TIMESTAMPTZ,
  language TEXT
);

CREATE TABLE seasons (
  id INTEGER PRIMARY KEY,
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  season_number INTEGER NOT NULL,
  name TEXT,
  overview TEXT,
  poster_path TEXT,
  air_date DATE,
  episode_count INTEGER
);

CREATE TABLE episodes (
  id INTEGER PRIMARY KEY,
  season_id INTEGER REFERENCES seasons (id) ON DELETE CASCADE,
  media_id INTEGER REFERENCES media (id) ON DELETE CASCADE,
  episode_number INTEGER NOT NULL,
  name TEXT,
  overview TEXT,
  still_path TEXT,
  air_date DATE,
  runtime INTEGER,
  vote_average NUMERIC(6, 3),
  vote_count INTEGER
);

CREATE INDEX idx_media_type ON media (media_type);
CREATE INDEX idx_media_collection ON media (collection_id);
CREATE INDEX idx_media_cast_person ON media_cast (person_id);
CREATE INDEX idx_media_crew_person ON media_crew (person_id);
CREATE INDEX idx_images_media ON images (media_id);
CREATE INDEX idx_videos_media ON videos (media_id);
CREATE INDEX idx_seasons_media ON seasons (media_id);
CREATE INDEX idx_episodes_season ON episodes (season_id);
CREATE INDEX idx_episodes_media ON episodes (media_id);
