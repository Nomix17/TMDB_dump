import gzip
import json
import shutil
from dotenv import load_dotenv
from parser import Parser
from dao import TMDB_DAO
from download_manager import downloadDailyExports
load_dotenv()

def decompressExports(exports:dict[str, str | None]) -> dict[str, str | None]:
  print("Decompressing the exports ...")
  paths_dict = {}
  for name, path in exports.items():
    if(path == None or not path.endswith(".gz")):
      paths_dict[name] = path 
      continue
    new_path = path.replace(".gz","")
    with gzip.open(path, 'rb') as f_in:
      with open(new_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    paths_dict[name] = new_path
  return paths_dict


def main() -> None:
  db = TMDB_DAO()
  parser = Parser(db)
  downloaded_exports = downloadDailyExports()
  decompressed_exports = decompressExports(downloaded_exports)

  if(decompressed_exports["movie_export_path"] != None):
    with open(decompressed_exports["movie_export_path"]) as json_file:
      for line in json_file:
        data = json.loads(line)
        if(data["id"]):
          parser.parse(data["id"], "movie")

  if(decompressed_exports["tv_export_path"] != None):
    with open(decompressed_exports["tv_export_path"]) as json_file:
      for line in json_file:
        data = json.loads(line)
        if(data["id"]):
          parser.parse(data["id"], "tv")

  if(decompressed_exports["person_export_path"] != None):
    with open(decompressed_exports["person_export_path"]) as json_file:
      for line in json_file:
        data = json.loads(line)
        if(data["id"]):
          parser.parse(data["id"], "person")


if __name__ == "__main__":
  main()
