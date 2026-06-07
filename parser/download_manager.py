import os
import gzip
import shutil
import requests
from urllib.request import urlretrieve
from urllib.error import HTTPError
from tqdm import tqdm
from datetime import datetime, timezone, timedelta

default_download_dir = "/tmp/ids_exports"
os.makedirs(default_download_dir, exist_ok=True)

def getLatestDate() -> str | None:
  print("Finding latest export date ...")
  target_date = datetime.now(timezone.utc)
  for _ in range(7):
    date_str = target_date.strftime("%m_%d_%Y")
    url = f"http://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"
    try:
      response = requests.head(url, timeout=5)
      if response.status_code == 200:
        print(f"Latest export date was {date_str}");
        return date_str
    except requests.RequestException:
      pass

    target_date -= timedelta(days=1)
  return None

def safeDownloadAnExport(file_name: str, attempt_number = 0) -> str | None:
  try:
    print(f"\nDownloading {file_name}, attempt_number = {attempt_number}")
    full_download_path = os.path.join(default_download_dir, file_name)
    if(os.path.exists(full_download_path)):
      if os.environ.get('RUNNING_IN_DOCKER', 'false').lower() == 'true':
        res = 'n'
      else:
        res = input(f"File already exists in {full_download_path}, do you want to redownload it? (y/N): ")
      if("n" in res.lower() or res.strip() == ""):
        return decompressExport(full_download_path)

    with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=file_name) as progress_bar:

      def progress_hook(count, block_size, total_size):
        if progress_bar.total is None and total_size > 0:
          progress_bar.total = total_size
        progress_bar.update(count * block_size - progress_bar.n)

      path, _ = urlretrieve (
        f"https://files.tmdb.org/p/exports/{file_name}",
        full_download_path,
        reporthook=progress_hook
      )
    return decompressExport(path)
    
  except HTTPError as e:
    print(f"\nError: failed to download {file_name}, error code: {e.code}, reason: {e.reason}")
    if e.code == 404 or attempt_number == 5:
      return None
    return safeDownloadAnExport(file_name, attempt_number + 1)

def decompressExport(export_path: str) -> str | None:
  print(f"Decompressing {export_path}  ...")
  if(export_path == None or not export_path.endswith(".gz")):
    return export_path
  new_path = export_path.replace(".gz","")
  with gzip.open(export_path, 'rb') as f_in:
    with open(new_path, 'wb') as f_out:
      shutil.copyfileobj(f_in, f_out)

  return new_path 

def downloadDailyExports() -> dict[str, str |None]:
  used_date = getLatestDate()
  movie_export_file = f"movie_ids_{used_date}.json.gz"
  tv_export_file = f"tv_series_ids_{used_date}.json.gz"
  person_export_file = f"person_ids_{used_date}.json.gz"

  return {
    "movie_export_path": safeDownloadAnExport(movie_export_file),
    "tv_export_path": safeDownloadAnExport(tv_export_file),
    "person_export_path": safeDownloadAnExport(person_export_file)
  }

