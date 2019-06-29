import argparse, pathlib, collections, multiprocessing, requests
from functools import partial

def download_data(filename:str, url:str, path:pathlib.Path) -> collections.Counter:
    req = requests.get(url+filename).content.decode('utf-8')
    (path/filename).write_text(req, 'utf-8')
    return collections.Counter(req)

def main(url:str, num_processes:int):
    # creating folder to store downloaded files 
    directory = pathlib.Path('files/')
    directory.mkdir(parents=True, exist_ok=True)
    # list of article names
    articles = open('files.txt', 'r').read().splitlines()
    # downloading and calculating symbols
    with multiprocessing.Pool(num_processes) as pool:
        articles_text_count = sum(pool.map(partial(download_data,url=url, path=directory),articles), collections.Counter())
    # replacing edge symbols
    articles_text_count['space'] = articles_text_count.pop(' ')
    articles_text_count['new_line'] = articles_text_count.pop('\n')
    # ccreation of result file
    with(directory.parent / 'result.txt').open('w', encoding='utf-8') as f:
      for key, value in articles_text_count.most_common():
        f.write(f'{key} {value}\n')

if __name__=='__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--url', type=str)
  parser.add_argument('--num_processes', type=int)
  args = parser.parse_args()
  main(args.url, args.num_processes)
