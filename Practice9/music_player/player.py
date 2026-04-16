import pygame

pygame.mixer.init()  # start the mixer so we can play sounds

tracks = ["music/track1.wav", "music/track2.wav"]  # list of track paths
current = 0  # index of the current track
is_playing = False

def play():
    global is_playing
    pygame.mixer.music.load(tracks[current])  # load the current track
    pygame.mixer.music.play()
    is_playing = True

def stop():
    global is_playing
    pygame.mixer.music.stop()
    is_playing = False

def next_track():
    global current
    current = current + 1
    if current >= len(tracks):  # go back to first if we passed the end
        current = 0
    play()

def prev_track():
    global current
    current = current - 1
    if current < 0:  # go to last if we went below zero
        current = len(tracks) - 1
    play()

def get_position():
    pos = pygame.mixer.music.get_pos()  # returns milliseconds
    seconds = pos // 1000
    return seconds
