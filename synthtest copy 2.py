import mido
import fluidsynth
import time
import numpy
import librosa
import wave
import resampy
import struct
import sys

from scipy.io.wavfile import read
from scipy.io.wavfile import write

from scipy import signal

from canne import *
import os

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s: %(message)s')

import re, os.path, time, textwrap
from sfz import SFZ
from sf2 import SF2

"""
TODO:
1. fix soundfont generation so harmonics are correct
2. include __main__() thing or some sort of correct initilization
3. implement multiprocessing
4. get fader working as cutoff freq
    a. cutoff freq should range from 300-1000 Hz

More TODO:
1. do more research on lowpass filter
    a. look at matlab butterworth filter
2. implement mini-canne
3. look into new datasets to use

"""


def lowpass_filter():

    sig = read("60.wav")
    sig_data = numpy.array(sig[1],dtype=float)


    fs = 44100
    order = 6
    cutoff = lowpass_filter_value

    nyquist = fs / 2
    b, a = signal.butter(order, cutoff / nyquist)
    if not np.all(np.abs(np.roots(a)) < 1):
        raise PsolaError('Filter with cutoff at {} Hz is unstable given '
                         'sample frequency {} Hz'.format(cutoff, fs))
    filtered = signal.filtfilt(b, a, sig_data, method='gust')


    write("60.wav", fs, filtered)

    print(filtered)

def generate_sfz():

    sfz = SFZ()
    regions = {}

    noteRegEx = re.compile('^(.+[-_])?(([abcdefgABCDEFG])([b#]?)(-?[0-9]))(v(([0-9]{1,3})|[LMHlmh]))?\.wav$')
    numRegEx = re.compile('^(.+[-_])?([0-9]{1,3})\.wav')

    notes = ['60.wav']#, 'note_72.wav', 'note_66.wav', 'note_78.wav']

    for fName in notes:
        match = noteRegEx.search(os.path.basename(fName))
        if match:
            noteNum = 96#sfz.convertNote(match.group(2))
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

    #print("Reading and processing input file...")
    if inputFormat == 'sfz':
        sfz = SFZ()
        if not sfz.importSFZ(inputFile):
            sys.exit(1)
        soundBank = sfz.soundBank

    #print("Writing output file...")
    if outputFormat == 'sfz':
        sfz = SFZ()
        sfz.soundBank = soundBank
        if not sfz.exportSFZ(outputFile):
            sys.exit(1)
    elif outputFormat == 'sf2':
        sf2 = SF2()
        if not sf2.exportSF2(soundBank, outputFile):
            sys.exit(1)

    #print("Done")


# initialize annesynth
mode = OperationMode(train=False,new_init=False,control=True)
synth = ANNeSynth(mode)
synth.load_weights_into_memory()


# Finds all ports with MIDI attachments
print(mido.get_input_names())


# Opens the port with the desired controller
control = 'KeyLab 88'
inport = mido.open_input(control)


# initialize fluidsynth
fs = fluidsynth.Synth(gain=0.20000000000000001)


# NOTE: may need to change driver depending on machine
fs.start(driver='coreaudio')


# load default instrument
sfid = fs.sfload("somesound.sf2") #if some crash happens and can't be loaded, change this to be test.sf2
fs.program_select(0, sfid, 0, 0)



notearray = []

div_fac = 100 # 31.75
offset = 5




# initialize fader values
tmp = numpy.zeros((1,9))

# faders 0-7 have range 0 to 4
# fader 8 has range -30 to 30
tmp[0,0] = offset
tmp[0,1] = offset
tmp[0,2] = offset
tmp[0,3] = offset
tmp[0,4] = offset
tmp[0,5] = offset
tmp[0,6] = offset
tmp[0,7] = offset
tmp[0,8] = offset

lowpass_filter_value = 2000



# TODO: convert the following into its own initilization function


"""generate a new sound"""
filename_= '60'
#synth.execute(tmp,filename_)


"""generate instrument from new sound"""
generate_sfz()
generate_sf2()


"""load new instrument"""
sfid = fs.sfload("somesound.sf2")
fs.program_select(0, sfid, 0, 0)


faderHasChanged = False

#fs.noteon(0, 60, 100)
#fs.noteon(0, 72, 100)

#time.sleep(1)
#fs.noteoff(0, 60)
#fs.noteoff(0, 72)

#time.sleep(10)

#new_process

#heyo = '60'
#generate_other_samples(heyo)



while True:
    msg = mido.Message('note_on')


    for new_msg in inport.iter_pending():

        msg = new_msg
        #print(msg)

        # TODO: add multiprocessing code to make if hasattr(...) and elif hasattr(...)
        #   contents running simultaneously (i.e. still playing while generating&loading new sound)



        if hasattr(msg, 'note'):

            #process this function

            #print(msg.note)

            # if faderHasChanged == True:

            #     # run generate_new_sound.py equivalent
            #     filename_= '60'
            #     synth.execute(tmp,filename_)

            #     # lowpass filter
            #     lowpass_filter()


            #     #generate_other_samples(filename_)

            #     # generate instrument from new sound
            #     generate_sfz()
            #     generate_sf2()

            #     # load new instrument
            #     sfid = fs.sfload("somesound.sf2")
            #     fs.program_select(0, sfid, 0, 0)

            #     faderHasChanged = False

            #     for note in notearray:
            #         fs.noteoff(0, note)
            #         fs.noteon(0, note, 100)
                

            if msg.type == 'note_on':
                fs.noteon(0, msg.note, msg.velocity)#msg.velocity)
                notearray.append(msg.note)
            elif msg.type == 'note_off':
                fs.noteoff(0, msg.note)
                notearray.remove(msg.note)

        elif hasattr(msg, 'control'):

            #store notes that are currently held down

            if msg.type == 'control_change':
                if msg.control == 73:
                    tmp[0,0] = offset + msg.value/div_fac
                    faderHasChanged = True

                elif msg.control == 75:
                    tmp[0,1] = offset + msg.value/div_fac
                    faderHasChanged = True

                elif msg.control == 79:
                    tmp[0,2] = offset + msg.value/div_fac
                    faderHasChanged = True

                elif msg.control == 72:
                    tmp[0,3] = offset + msg.value/div_fac
                    faderHasChanged = True

                # elif msg.control == 80:
                #     tmp[0,4] = offset + msg.value/div_fac
                #     faderHasChanged = True

                # elif msg.control == 81:
                #     tmp[0,5] = offset + msg.value/div_fac
                #     faderHasChanged = True

                # elif msg.control == 82:
                #     tmp[0,6] = offset + msg.value/div_fac
                #     faderHasChanged = True

                # elif msg.control == 83:
                #     tmp[0,7] = offset + msg.value/div_fac
                #     faderHasChanged = True

                # TODO: map 9th fader to lowpass filter cutoff freq
                
                elif msg.control == 85:
                    # lowpass filter with cutoff freq,

                    lowpass_filter_value = 2000 - msg.value*10

                    #print("lowpass_filter_value")
                    #print(lowpass_filter_value)

                    lowpass_filter()#msg.value*5)

                    generate_sfz()
                    generate_sf2()

                    # load new instrument
                    sfid = fs.sfload("somesound.sf2")
                    fs.program_select(0, sfid, 0, 0)
                    # generate
                    # load

                    # remove next 4 lines

                #    if msg.value == 127:
                #        tmp[0,8] = 6*5
                #    else:
                #        tmp[0,8] = (msg.value-63)/10.5*5

                    faderHasChanged = True


            #print(tmp)

        if hasattr(msg, 'pitch'):
            fs.pitch_bend(0, msg.pitch)

        if faderHasChanged == True:

            # wait 10 seconds
            # if (there are no more mido messages)
                # ^ do this check without removing mido messages

                # do the stuff

            # if there is a mido message...


            # run generate_new_sound.py equivalent
            start = time.time()
            filename_= '60'
            synth.execute(tmp,filename_)
            end = time.time()
            print('canne time: ' + str(end - start))


            start = time.time()
             # lowpass filter
            #lowpass_filter()
            end = time.time()
            print('lowpass time: ' + str(end - start))

           


            #generate_other_samples(filename_)

            # generate instrument from new sound

            start = time.time()
            generate_sfz()
            end = time.time()
            print('sfz time: ' + str(end - start))

            start = time.time()
            generate_sf2()
            end = time.time()
            print('sf2 time: ' + str(end - start))

            # load new instrument
            start = time.time()
            sfid = fs.sfload("somesound.sf2")
            fs.program_select(0, sfid, 0, 0)
            end = time.time()
            print('fs time: ' + str(end - start))

            faderHasChanged = False

            for note in notearray:
                fs.noteoff(0, note)
                fs.noteon(0, note, 100)



fs.delete()




