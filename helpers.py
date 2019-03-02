from contextlib import contextmanager
from lyricsmaster.utils import normalize
import sys, os


@contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Eliminates extra 'Lyricsmaster' nested folder
def song_save_override(self, folder):
    if not folder:
        folder = os.path.join(os.path.expanduser("~"), 'Documents', 'LyricsMaster')
    if self.lyrics:
        artist = normalize(self.artist)
        album = normalize(self.album)
        save_path = os.path.join(folder, artist, album)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_name = normalize(self.title)
        with open(os.path.join(save_path, file_name + ".txt"), "w", encoding="utf-8") as file:
            file.write(self.lyrics)