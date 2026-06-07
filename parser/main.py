import json
from dotenv import load_dotenv
from parser import Parser
from dao import TMDB_DAO
from download_manager import downloadDailyExports
load_dotenv()

def processJsonLines(parser, export_path, mediaType):
  if(export_path != None):
    with open(export_path) as json_file:
      for line in json_file:
        data = json.loads(line)
        if(data.get("id")):
          parser.fetchAndStore(data["id"], mediaType)

def dumpTMDB(parser):
  downloaded_exports = downloadDailyExports()
  processJsonLines(parser, downloaded_exports["movie_export_path"], "movie")
  processJsonLines(parser, downloaded_exports["tv_export_path"], "tv")
  processJsonLines(parser, downloaded_exports["person_export_path"], "person")

def main() -> None:
  db = TMDB_DAO()
  parser = Parser(db)
  dumpTMDB(parser)

if __name__ == "__main__":
  main()
