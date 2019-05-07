import mido

import fluidsynth

import time

import numpy
import librosa
import wave
import resampy
import struct

import sys
from canne import *
import os

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s: %(message)s')

import re, os.path, time, textwrap
from sfz import SFZ
from sf2 import SF2

#noteList = [60, 66, 72, 78]
noteList = [60]

def generate_other_samples(fn):
    
    fn = fn + '.wav'

    for i in noteList:
        print(i)
        sr_orig = int(44100/(2**((-i+60)/12)))

        x, sr_origignore = librosa.load(fn, sr=None)

        y_low = resampy.resample(x, sr_orig, 44100)
        print(y_low)

        scaled_y_low = [i * 32767 for i in y_low]

        fileToWrite = wave.open('note_' + str(i) + '.wav', 'wb')
        fileToWrite.setparams((1, 2, 44100, len(x), 'NONE', 'UNCOMPRESSED')) # 1:numChan, 2: dataSize
        for j in scaled_y_low:
            value = int(j)
            data = struct.pack('<h', value)
            fileToWrite.writeframesraw(data)
        fileToWrite.close()



def generate_sfz():

    sfz = SFZ()
    regions = {}

    noteRegEx = re.compile('^(.+[-_])?(([abcdefgABCDEFG])([b#]?)(-?[0-9]))(v(([0-9]{1,3})|[LMHlmh]))?\.wav$')
    numRegEx = re.compile('^(.+[-_])?([0-9]{1,3})\.wav')

    notes = ['note_60.wav']#, 'note_72.wav', 'note_66.wav', 'note_78.wav']

    for fName in notes:
        match = noteRegEx.search(os.path.basename(fName))
        if match:
            noteNum = sfz.convertNote(match.group(2))
            if noteNum == None:
                logging.warning("`Can't guess pitch from file name: {}".format(fName))
                continue
            regions[noteNum] = fName
            continue
        match = numRegEx.search(os.path.basename(fName))
        if match:
            noteNum = int(match.group(2))
            if noteNum < 0 or noteNum > 127:
                logging.warning("Can't guess pitch from file name: {}".format(fName))
                continue
            regions[noteNum] = fName
        logging.warning("Can't guess pitch from file name: {}".format(fName))

    soundBank = {
    'Name': 'Unnamed sound bank',
    'Date': time.strftime("%Y-%m-%d"),
    'instruments': [{
        'Instrument': 'Unnamed instrument',
        'ampeg_release': '0.5',
        'groups': [{
            'loop_mode': 'loop_continuous',
            'regions': []
            }]
        }]
    }

    prevRegion = None
    for noteNum in sorted(regions.keys()):
        region = {}
        region['sample'] = regions[noteNum]
        region['pitch_keycenter'] = noteNum
        if prevRegion:
            gap = noteNum - prevRegion['pitch_keycenter'] - 1
            leftGap = gap // 2
            rightGap = gap - leftGap
            prevRegion['hikey'] = prevRegion['pitch_keycenter'] + leftGap
            region['lokey'] = noteNum - rightGap
        soundBank['instruments'][0]['groups'][0]['regions'].append(region)
        prevRegion = soundBank['instruments'][0]['groups'][0]['regions'][-1]

    sfz.soundBank = soundBank
    sfz.exportSFZ('somesound.sfz')

def generate_sf2():

    inputFile = 'somesound.sfz'
    inputFormat = 'sfz'
    outputFile = 'somesound.sf2'
    outputFormat = 'sf2'
    soundBank = None

    print("Reading and processing input file...")
    if inputFormat == 'sfz':
        sfz = SFZ()
        if not sfz.importSFZ(inputFile):
            sys.exit(1)
        soundBank = sfz.soundBank

    print("Writing output file...")
    if outputFormat == 'sfz':
        sfz = SFZ()
        sfz.soundBank = soundBank
        if not sfz.exportSFZ(outputFile):
            sys.exit(1)
    elif outputFormat == 'sf2':
        sf2 = SF2()
        if not sf2.exportSF2(soundBank, outputFile):
            sys.exit(1)

    print("Done")



#can maybe remove this function
def wav_to_floats(wave_file):
    w = wave.open(wave_file)
    astr = w.readframes(w.getnframes())
    # convert binary chunks to short 
    a = struct.unpack("%ih" % (w.getnframes()* w.getnchannels()), astr)
    a = [float(val) / pow(2, 15) for val in a]
    return a

mode = OperationMode(train=False,new_init=False,control=True)
synth = ANNeSynth(mode)
synth.load_weights_into_memory()

# Finds all ports with MIDI attachments
#print(mido.get_input_names())

# Opens the port with the desired controller
#control = 'KeyLab 88'
#inport = mido.open_input(control)


fs = fluidsynth.Synth()

# NOTE: may need to change driver depending on machine
fs.start(driver='coreaudio')

sfid = fs.sfload("somesound.sf2") #if some crash happens and can't be loaded, change this to be test.sf2
fs.program_select(0, sfid, 0, 0)

tmp = numpy.zeros((1,9))
# faders 0-7 have range 0 to 4
# fader 8 has range -30 to 30
tmp[0,0] = 2
tmp[0,1] = 2
tmp[0,2] = 2
tmp[0,3] = 2
tmp[0,4] = 2
tmp[0,5] = 2
tmp[0,6] = 2
tmp[0,7] = 2
tmp[0,8] = 0

fs.noteon(0, 40, 100)

time.sleep(1.0)

fs.noteon(0, 45, 100)

time.sleep(1.0)

fs.noteon(0, 47, 100)

time.sleep(1.0)

fs.noteon(0, 52, 100)

time.sleep(1.0)

fs.noteon(0, 51, 100)

time.sleep(1.0)

fs.noteoff(0, 40)
fs.noteoff(0, 45)
fs.noteoff(0, 47)
fs.noteoff(0, 52)
fs.noteoff(0, 51)

