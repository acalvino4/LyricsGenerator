from helpers import suppress_output, song_save_override
from markov_python.cc_markov import MarkovChain
import lyricsmaster

import random, os, sys

# encoding=utf8
# reload(sys)
# sys.setdefaultencoding('utf8')

lyricsmaster.models.Song.save = song_save_override 

class song_generator(object):
    with suppress_output():
        provider = lyricsmaster.providers.Genius()
    
    def __init__(self, artist):
        # download discography if not already downloaded
        artist_path = os.path.join('cached-lyrics', lyricsmaster.utils.normalize(artist))
        if not os.path.exists(artist_path):
            print("Downloading albums...")
            with suppress_output():
                self.discography = song_generator.provider.get_lyrics(artist)
            if not self.discography:
                raise KeyError('Artist: ' + artist + ' not found in database.')
            print("Download finished.")
            self.discography.save('cached-lyrics')
        print("Loading lyrics to generator...")
        album_list = os.listdir(artist_path)
        # initialize mc generators
        self.artist = artist
        self.mc_album_title = MarkovChain(1)
        self.mc_song_title = MarkovChain(1)
        self.mc_lyrics = MarkovChain(2)

        for album in album_list:
            self.mc_album_title.add_string(album.replace('-',' '))
            album_path = os.path.join(artist_path,album)
            song_list = os.listdir(album_path)
            for song in song_list:
                if song:
                    song_path = os.path.join(album_path, song)
                    self.mc_song_title.add_string(os.path.splitext(song)[0].replace('-',' '))
                    self.mc_lyrics.add_file(song_path)
        print("Loading complete.")
            
    def song_title(self):
            title = ' '.join([word.capitalize() for word in self.mc_song_title.generate_text(random.randrange(2,7))])
            return title

    def song_lyrics(self):
        chorus = self.song_stanza()
        # this line alternates new verses with chorus
        verses_and_chorus = [self.song_stanza() if i%2==0 else chorus for i in range(6)]
        lyrics = '\n'.join(verses_and_chorus)
        return lyrics
    
    def song_stanza(self):
        words = self.mc_lyrics.generate_text(32)
        stanza = ''
        for i in range(4):
            stanza += ' '.join(words[i*8:i*8+8]).capitalize() + '\n'
        return stanza

    # Songs made outside an album get added to default 'Singles' album
    def make_song(self, album='Singles', save=False):
        title = self.song_title()
        album = album
        artist = self.artist
        lyrics = self.song_lyrics()
        song = lyricsmaster.models.Song(title, album, artist, lyrics)
        if save:
            song.save('new-lyrics')
        return song

    def album_title(self):
        album_title = ' '.join([word.capitalize() for word in self.mc_album_title.generate_text(4)])
        return album_title

    def make_album(self, save=False):
        num_songs = random.randrange(4,12)
        title = self.album_title()
        artist = self.artist
        songs = [self.make_song(title, save=save) for i in range(num_songs)]
        album = lyricsmaster.models.Album(title, artist, songs)
        return album
