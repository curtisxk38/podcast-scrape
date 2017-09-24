import requests
from bs4 import BeautifulSoup

from os import path, listdir
import argparse
import sys

class PodcastScraper:
    def __init__(self, output_path):
        self.output = output_path
        self.BUFFER_SIZE = 16384
        self.PROGRESS_BAR = 40

    def main(self):
        url = "https://rss.art19.com/road-trippin-with-rj-and-channing"
        r = requests.get(url)
        bs = BeautifulSoup(r.content, "lxml")
        episodes = bs.find_all("item")
        
        already_downloaded = [f for f in listdir(self.output) if path.isfile(path.join(self.output, f))]
        to_download = []
        
        for ep in episodes:
            title = ep.title.string.strip()
            name = self.file_name(title)
            if name not in already_downloaded:
                url = ep.enclosure["url"]
                to_download.append((title, name, url))

        for i, tup in enumerate(to_download):
            title, name, url = tup
            print("Downloading {}/{}: {}".format(i + 1, len(to_download), title))
            self.download_episode(url, name)


    def download_episode(self, url, file_name):
        mp3 = requests.get(url, stream=True)
        size = int(mp3.headers["Content-Length"].strip())

        with open(path.join(self.output, file_name), "wb") as f:
            for chunk in self.progress_bar(mp3.iter_content(self.BUFFER_SIZE), size):
                f.write(chunk)

    def progress_bar(self, it, size):
        count = size / self.BUFFER_SIZE
        size_mb = size / 1e6
        def _show(_i):
            x = int(self.PROGRESS_BAR * _i / count)
            sys.stdout.write("[{}{}] {:.2f}/{:.2f} Mb\r".format("#" * x,  "." * (self.PROGRESS_BAR - x), _i * self.BUFFER_SIZE / 1e6, size_mb))

        _show(0)
        for i, item in enumerate(it):
            yield item
            _show(i + 1)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def file_name(self, episode_name):
        return "{}.mp3".format(episode_name.replace("/", ""))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", required=True, help="Path to directory to output files to")
    args = ap.parse_args()
    PodcastScraper(args.output_path).main()

    