from __future__ import division
from Tkinter import *
import math
import pyaudio
import wave
import sys
from aubio import source, onset, pitch
import copy
import string
from aubio import source, tempo
import numpy
from numpy import median, diff
####################################


####################################
def init(data):
    data.startScreen=True
    data.recordScreen=False
    data.showMusicScreen=False
    data.recordWindow=False
    data.errorMessageRecordFirst=False
    data.errorMessagePickFirst=False
    data.helpScreen=False
    data.trebleSelected=False
    data.bassSelected=False
    data.pitch=pitch
    data.clef="treble" #temporary before user inputs this
    data.lines=5 #temporary before getMeasuresAndLines
    data.timeSignature=(4,2) #temporary before user inputs this
    data.sideBarWidth=data.width//6
    data.marginFromSideBar=10
    data.sheetBorderLeft=data.sideBarWidth+data.marginFromSideBar
    data.sheetBorderRight=data.width-data.marginFromSideBar
    data.sheetBorderTop=data.marginFromSideBar
    data.sheetBorderBottom=data.height-data.marginFromSideBar
    data.marginStaffFromSideBorder=100
    data.marginStaffFromTopBorder=100
    data.lineSeparation=10 
    data.staffSeparation=50
    data.measureWidth=data.width//6
    data.noteWidth=data.measureWidth//32
    data.noteHeight=data.lineSeparation//2
    data.stemHeight=3.5*data.lineSeparation
    data.wholeNoteInsideShrink=0.6
    data.dotDistance=6
    data.dotRadius=data.noteWidth//3
    data.beatsDrawn=0
    data.notesDrawn=[]
    data.wholeNoteInsideShrink=0.63
    data.dotRadius=data.noteWidth//3
    data.clefWidth=data.measureWidth//5
    data.sideBarButtonsDistance=data.height//10
    data.recordTitle=""
    data.recordSeconds=0
    data.noteBounds=[]
    data.noteSelected=[]
    data.drawFirstTime=True
    data.dx=0
def mousePressed(event, data):
    #checks if clicked the rectangle in the first screen
    if (event.x>data.startRectanglex1 and event.x<data.startRectanglex2 
        and event.y>data.startRectangley1 and event.y<data.startRectangley2 and data.startScreen):
        data.recordScreen=True
        data.startScreen=False

    #checks if clicked help button
    if (event.x>data.helpButtonLeft and  event.x<data.helpButtonRight and event.y>data.helpButtonTop 
        and event.y<data.helpButtonBottom):
        data.helpScreen=not data.helpScreen #toggles on and off

    #checks if clicked record button. doesn't work on help screen
    if (data.recordScreen and  not data.helpScreen and event.x>data.recordButtonCenterx-data.recordButtonOuterRadius and 
        event.y>data.recordButtonCentery-data.recordButtonOuterRadius and 
        event.x<data.recordButtonCenterx+data.recordButtonOuterRadius and 
        event.y<data.recordButtonCentery+data.recordButtonOuterRadius):
        #checks if user has selected all 3 options
        if data.timeSignature!=(4,2) and data.recordSeconds!=0 and not (data.trebleSelected==False and data.bassSelected==False):
            data.recordWindow=True #creates the popup
        else:
            data.errorMessagePickFirst=True
        
    #checks if clicked sheet music button. doesn't work on help screen
    if (not data.helpScreen and event.x>data.musicButtonCenterx-data.musicButtonOuterRadius and 
        event.y>data.musicButtonCentery-data.musicButtonOuterRadius and 
        event.x<data.musicButtonCenterx+data.musicButtonOuterRadius and 
        event.y<data.musicButtonCentery+data.musicButtonOuterRadius and 
        data.recordScreen):
        if data.recordTitle!="": #checks if user has recorded something
            analyzeRecording(data)
            data.showMusicScreen=True
        else: 
            data.errorMessageRecordFirst=True

    #checks if clicked treble clef box. doesn't work on help screen
    if (event.x>data.trebleBoxLeft and not data.helpScreen and event.x<data.trebleBoxRight
        and event.y>data.trebleBoxTop and event.y<data.trebleBoxBottom):
        data.trebleSelected=True
        data.bassSelected=False
        data.clef="treble"

    #checks if clicked bass clef box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.bassBoxLeft and event.x<data.bassBoxRight
        and event.y>data.bassBoxTop and event.y<data.bassBoxBottom):
        data.trebleSelected=False
        data.bassSelected=True
        data.clef="bass"

    #checks if clicked (4,4) box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.timeSigBox1Left and event.x<data.timeSigBox1Right
        and event.y>data.timeSigBox1Top and event.y<data.timeSigBox1Bottom): #box 1 is (4,4)
        data.timeSignature=(4,4)
        data.noteSeparationInMeasure=data.measureWidth/(data.timeSignature[0]) #spaces notes based on time sig

    #checks if clicked (3,4) box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.timeSigBox2Left and event.x<data.timeSigBox2Right
        and event.y>data.timeSigBox2Top and event.y<data.timeSigBox2Bottom): #box 1 is (3,4)
        data.timeSignature=(3,4)
        data.noteSeparationInMeasure=data.measureWidth/(data.timeSignature[0])#note spacing

    #checks if clicked 5 sec record box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.sec5BoxLeft and
        event.x<data.sec5BoxRight and event.y>data.sec5BoxTop and
        event.y<data.sec5BoxBottom):
        data.recordSeconds=5

    #checks if clicked 10 sec record box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.sec10BoxLeft and
        event.x<data.sec10BoxRight and event.y>data.sec10BoxTop and
        event.y<data.sec10BoxBottom):
        data.recordSeconds=10

    #checks if clicked 20 sec record box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.sec20BoxLeft and
        event.x<data.sec20BoxRight and event.y>data.sec20BoxTop and
        event.y<data.sec20BoxBottom):
        data.recordSeconds=20

    #checks if clicked 30 sec record box. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.sec30BoxLeft and
        event.x<data.sec30BoxRight and event.y>data.sec30BoxTop and
        event.y<data.sec30BoxBottom):
        data.recordSeconds=30

    #checks if clicked playback button. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.playButtonLeft and 
        event.x<data.playButtonRight and event.y>data.playButtonTop and 
        event.y<data.playButtonBottom):
        playBack(data)

    #checks if clicked back button. doesn't work on help screen
    if (data.recordScreen and not data.helpScreen and event.x>data.backButtonLeft and event.x<data.backButtonRight
        and event.y>data.backButtonTop and event.y<data.backButtonBottom):
        data.recordScreen=False
        data.showMusicScreen=False
        data.startScreen=True

    #checks if clicked a note
    if data.showMusicScreen:
        for i in range(len(data.noteBounds)): #loops through bounds of notes
            bounds=data.noteBounds[i]
            left=bounds[0]
            top=bounds[1]
            right=bounds[2]
            bottom=bounds[3]
            if event.x>left and event.x<right and event.y>top and event.y<bottom:
                data.noteSelected=[bounds,i]

def keyPressed(event, data):
    if data.noteSelected!=[]:
        if event.keysym=="Up":
            editNote(data, +1)
        if event.keysym=="Down":
            editNote(data, -1)

def timerFired(data):
    pass
##########################################################

def editNoteUpB(data,dy, octavesUp, octavesDown):
    newNoteName="c"
    if octavesUp!=0 or (octavesUp==0 and octavesDown==0):
        octavesUp+=1 #add another bc c is next octave up
        for i in range(octavesUp):
            newNoteName+="'"
    if octavesDown !=0:
        octavesDown-=1 # remove because c is next octave up
        for i in range(octavesDown):
            newNoteName+=","
    return newNoteName

def editNoteDownC(data, dy, octavesUp,octavesDown):
    newNoteName="b"
    if octavesUp!=0:
        octavesUp-=1 #remove an octave bc b is octave below
        for i in range(octavesUp):
            newNoteName+="'"
        return newNoteName
    if octavesDown !=0 or (octavesUp==0 and octavesDown==0):
        octavesDown+=1 #add an octave bc b is octave below
        for i in range(octavesDown):
            newNoteName+=","
    return newNoteName

def editNoteUpG(data, dy, octavesUp, octavesDown):
    newNoteName="a" #need this because it would go to "h" otherwise
    if octavesUp!=0:
        for i in range(octavesUp):
            newNoteName+="'"
    if octavesDown !=0:
        for i in range(octavesDown):
            newNoteName+=","
    return newNoteName

def editNoteDownA(data, dy, octavesUp, octavesDown):
    newNoteName="gis" #need this because it would go to some other ascii character otherwise
    if octavesUp!=0:
        for i in range(octavesUp):
            newNoteName+="'"
    if octavesDown !=0:
        for i in range(octavesDown):
            newNoteName+=","
    return newNoteName

def editNote(data, dy):
    #changes note name and edits data.notes destructively
    listPos=data.noteSelected[1]
    currNote=data.notes[listPos] #tuple of note length, note name
    noteLength, noteName=currNote
    octavesUp, octavesDown=0,0
    if noteName!="rest":
        if "'" in noteName:
            octavesUp=noteName.count("'")
        if "," in noteName:
            octavesDown=noteName.count(",")
    if noteName[0]=="b" and dy==1:
        newNoteName=editNoteUpB(data,dy, octavesUp,octavesDown)
    elif noteName[0]=="c" and dy==-1 and "is" not in noteName:
        newNoteName=editNoteDownC(data,dy,octavesUp, octavesDown)
    elif noteName[0]=="g" and dy==1 and "is" in noteName:
        newNoteName=editNoteUpG(data, dy, octavesUp, octavesDown)
    elif noteName[0]=="a" and dy==-1 and "is" not in noteName:
        newNoteName=editNoteDownA(data, dy, octavesUp, octavesDown)
    elif noteName!="rest":
        currLetter=noteName[0]
        #calculates new note letter
        if dy==1:
            if (("is" not in noteName) and (noteName[0]=="c" 
                or noteName[0]=="d" or noteName[0]=="f" or noteName[0]=="g" 
                or noteName[0]=="a")): #accounts for sharps
                newNoteName=noteName[0]
                newNoteName+="is"
            else:
                newNoteName=chr(ord(currLetter)+1)
        if dy==-1:
            if "is" in noteName: #accounts for sharps
                newNoteName=noteName[0]
            else:
                newNoteName=chr(ord(currLetter)-1)
                if (noteName[0]=="d" or noteName[0]=="g" or noteName[0]=="a" or noteName[0]=="b" or noteName[0]=="e"):
                    newNoteName+="is"
        #changes octaves accordintly
        if octavesUp!=0:
            for i in range(octavesUp):
                newNoteName+="'"
        if octavesDown!=0:
            for i in range(octavesDown):
                newNoteName+=","
    if data.clef=="treble": #don't let note go lower/ higher than a specific note
        if (newNoteName=="f'''" and dy==1) or (newNoteName=="e" and dy==-1):
            return 
    if data.clef =="bass": #don't let note go lower/ higher than a specific note
        if (newNoteName=="g,," and dy==-1) or (newNoteName=="g'" and dy==1):
            return 
    newTuple=(noteLength, newNoteName)
    data.noteBounds=[]
    data.drawFirstTime=True
    data.notes[listPos]=newTuple #destructively modify becuase drawing and playback based on this

##########################################################
def formatRecordTitle(data): #takes away whitespace and makes it into a .wav
    if data.recordTitle=="":
        data.recordTitle="default.wav"
        data.sheetMusicTitle="Default"
    else:
        newString=""
        if data.recordTitle.endswith(".wav"):
            data.sheetMusicTitle=data.recordTitle[:-4]
            for letter in data.recordTitle[:-4]:
                if (letter in string.ascii_letters) or (letter in string.digits):
                    newString+=letter
        else:
            data.sheetMusicTitle=data.recordTitle
            for letter in data.recordTitle:
                if (letter in string.ascii_letters) or (letter in string.digits):
                    newString+=letter
        newString+=".wav"
        data.recordTitle=newString
    
def reverseDictionary(dictionary):
        newDict={}
        for key in dictionary:
            newKey=dictionary[key]
            newDict[newKey]=key
        return newDict

def record(data, recordTitle):
    #taken from https://people.csail.mit.edu/hubert/pyaudio/
    data.recordTitle=recordTitle.get() #i added this 
    formatRecordTitle(data) #i added this 
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = data.recordSeconds #i edited this
    WAVE_OUTPUT_FILENAME = data.recordTitle #i edited this
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording") 
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

#########################################################

##########################################################
def recordWindow(canvas, data):
    #referenced from tkinter widget manual
    #popup window that asks user to record
    height=data.height//5
    width=data.width//2
    top=Toplevel()
    top.title("Record")
    frame=Frame(top, height=height, width=width)
    frame.pack()
    recordMessage=Message(top, text="Enter a title name and click record when ready")
    recordMessage.pack()
    #starts recording
    recordTitle=Entry(top)
    recordTitle.pack()
    recordTitle.focus_set()
    button=Button(top, text="Record", command=lambda: record(data, recordTitle) )
    button.pack(side=LEFT)
    #stops recording
    data.recordWindow=False

def getBPM(data ,path):
    #taken from aubio github https://github.com/aubio/aubio/blob/master/python/demos/demo_bpm_extract.py
    samplerate, win_s, hop_s = 44100, 1024, 512
    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
            #if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break
    # Convert to periods and to bpm 
    if len(beats) > 1:
        bpms = 60./diff(beats)
        b = median(bpms)
    else:
        b = 60 #set this to default 60
    data.bpm=int(b) #added this

def analyzeRecording(data):
    #this part is taken from aubio github - https://github.com/aubio/aubio/blob/master/python/demos/demo_pitch.py
    filename=data.recordTitle #added this
    getBPM(data, filename) #added this
    downsample = 1
    samplerate = 44100 // downsample
    if len( sys.argv ) > 2: samplerate = int(sys.argv[2])
    win_s = 4096 // downsample # fft size
    hop_s = 512  // downsample # hop size
    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate
    tolerance = 0.8
    pitch_o = data.pitch("yinfft", win_s, hop_s, samplerate)
    pitch_o.set_unit("Hz")
    pitch_o.set_tolerance(tolerance)
    pitches = []
    confidences = []
    # total number of frames read
    total_frames = 0
    timesAndPitches=[]
    while True:
        samples, read = s()
        pitch = pitch_o(samples)[0]
        #pitch = int(round(pitch))
        confidence = pitch_o.get_confidence()
        if confidence < 0.8: pitch = None #edited this
        if pitch!=None:
            # print("%f %f %f" % (total_frames / float(samplerate), pitch, confidence))
            pitches += [pitch]
            time=total_frames/float(samplerate)#added this
            timesAndPitches.append((time, pitch)) #added this
            
        confidences += [confidence]
        total_frames += read
        if read < hop_s: break
    if 0: sys.exit(0)

    def filteredTimesAndPitchesStartTimes(timesAndPitches, pitches):
        #finds the start times of different notes
        UPPER_DEVIATION=150 #checks if huge change
        LOWER_DEVIATION=5 #checks if its the same note being held down (don't want to include more than once)
        filteredPitches=[]
        filteredPitchesAndTimes=[]
        for i in range(len(pitches)-1):
            if filteredPitches==[]:
                filteredPitches.append(pitches[i])
                filteredPitchesAndTimes.append(timesAndPitches[i])
            elif abs(pitches[i]-filteredPitches[-1])>LOWER_DEVIATION:
                filteredPitches.append(pitches[i])
                filteredPitchesAndTimes.append(timesAndPitches[i])
        return filteredPitchesAndTimes
    filteredTimesAndPitchesStartTimes=filteredTimesAndPitchesStartTimes(timesAndPitches, pitches)
   
    def filteredTimesAndPitchesEndTimes(timesAndPitches, pitches, filteredTimesAndPitchesStartTimes):
        #finds end times of different notes
        filteredTimesAndPitchesEndTimes=[] #place holder to make lengths of start times and end times the same
        for i in range(1, len(filteredTimesAndPitchesStartTimes)):
            nextTime=filteredTimesAndPitchesStartTimes[i][0]
            for i in range(len(timesAndPitches)):
                if nextTime==timesAndPitches[i][0]:
                    filteredTimesAndPitchesEndTimes.append(timesAndPitches[i-1])
        return filteredTimesAndPitchesEndTimes
    filteredTimesAndPitchesEndTimes=filteredTimesAndPitchesEndTimes(timesAndPitches, pitches, filteredTimesAndPitchesStartTimes)
 
    def getNoteLengths(filteredTimesAndPitchesStartTimes, filteredTimesAndPitchesEndTimes):
        #finds lengths by subtracting end times from start times
        noteLengths=[]
        for i in range(len(filteredTimesAndPitchesEndTimes)):
            length=filteredTimesAndPitchesEndTimes[i][0]-filteredTimesAndPitchesStartTimes[i][0]
            if length>0.08:
                noteLengths.append((length, filteredTimesAndPitchesStartTimes[i][1]))
        if filteredTimesAndPitchesStartTimes[-1]!=0:
            noteLengths.append((data.recordSeconds-filteredTimesAndPitchesStartTimes[-1][0], filteredTimesAndPitchesStartTimes[-1][1]))
        else:
            length=filteredTimesAndPitchesStartTimes[i+1][0]-filteredTimesAndPitchesStartTimes[i][0]
            noteLengths.append(length, filteredTimesAndPitchesStartTimes[i][1])
        return noteLengths
    noteLengths=getNoteLengths(filteredTimesAndPitchesStartTimes, filteredTimesAndPitchesEndTimes)
 
    frequenciesToNotesDictionary={0.0: "rest", 16.35: "c,,,", 17.32: "cis,,," ,18.35:"d,,,",
        19.45 :"dis,,," , 
        20.60: "e,,,", 21.83:"f,,,", 23.12 :"fis,,,", 24.50: "g,,,", 25.96: "gis,,,", 27.50:"a,,,", 
        29.14:"ais,,,", 30.87:"b,,,", 32.70: "c,,", 34.65: "cis,,", 36.71: "d,,", 38.89: "dis,,", 41.20: "e,,", 43.65: "f,,",46.25:"fis,,", 49.00:"g,,", 51.91:"gis,,", 
        55.00:"a,,", 58.27:"ais,,", 61.74:"b,,", 65.41:"c,", 69.30: "cis,", 73.42:"d,", 
        77.78:"dis,", 82.41:"e,", 87.31:"f,", 92.50:"fis,", 98.00:"g,",103.83: "gis,", 
        110.00:"a,",116.54:"ais,", 123.47:"b,", 130.81:"c", 138.59:"cis", 146.83:"d", 
        155.56:"dis", 164.81: "e", 174.61: "f", 185.00:"fis", 196.00:"g", 207.65:"gis", 
        220.00:"a", 233.08:"ais", 246.94:"b", 261.63:"c'", 277.18:"cis'", 293.66:"d'",
        311.13:"dis'", 329.63:"e'", 349.23:"f'", 369.99:"fis'", 392.00:"g'", 415.30:"gis'",
        440.00:"a'", 466.16:"ais'", 493.88:"b'", 523.25:"c''", 554.37:"cis''", 587.33:"d''",
        622.25:"dis''", 659.26:"e''", 698.46:"f''", 739.99:"fis''", 783.99:"g''", 830.61:"gis''", 
        880.00:"a''", 932.33:"ais''", 987.77:"b''", 1046.50:"c'''", 1108.73: "cis'''", 1174.66: "d'''", 1244.51:"dis'''",
        1318.51:"e'''", 1396.91:"eis'''", 1479.98:"fis'''", 1567.98:"g'''", 1661.22:"gis'''", 1760.00:"a'''", 
        1864.66:"ais'''", 1975.53:"b'''", 2093.00:"c''''", 2217.46:"cis''''", 2349.32:"d''''", 2489.02:"dis''''",
        2637.02:"e''''", 2793.83: "f''''", 2959.96:"fis''''", 3135.96:"g''''", 3322.44:"gis''''",
        3520.00:"a''''", 3729.31:"ais''''", 3951.07:"b''''", 4186.01:"c'''''", 4434.92:"cis'''''",
        4698.64:"d'''''", 4978.03:"dis'''''", 5274.04:"e'''''", 5587.65:"f'''''", 5919.91:"fis'''''",
        6271.93:"g'''''", 6644.88:"gis'''''", 7040.00:"a'''''", 7458.62:"ais''''", 7902.13:"b'''''"}
    notesList=[]
    data.frequenciesToNotesDictionary=frequenciesToNotesDictionary

    def frequenciesToNotes(cleanNoteLengths):
        #maps frequencies to note names from dictionary
        closestDistance=100000 #set to a big number because it keeps track of which note its closest to
        note=None
        frequencyToNote=[] #list of tuples instead of dictionary bc notes might repeat
        for timePitchTuple in cleanNoteLengths:
            pitch=timePitchTuple[1]
            time=timePitchTuple[0]
            for frequency in frequenciesToNotesDictionary:
                if abs(pitch-frequency)<closestDistance: #checks which frequency in the dictionary it is closest to
                    closestDistance=abs(pitch-frequency)
                    note=frequenciesToNotesDictionary[frequency]
            frequencyToNote.append((time,note))
            notesList.append(note)
            closestDistance=100000 #reset this at end of looping through dictionary
            note=None
        return frequencyToNote
    frequencyToNote=frequenciesToNotes(noteLengths)
    
    def cleanNoteNames(frequencyToNote, data):
        #adds together notes that are close togehter that mightve been separated by an accidental pause
        #gets rid of accidental pauses so there aren't unnecessary rests
        bpm=data.bpm
        quarter=60.0/bpm
        cleanNoteNames=[]
        i=0
        while i+1<len(frequencyToNote):
            if frequencyToNote[i][1]==frequencyToNote[i+1][1]: #if theyre equal, add them together
                totalTime=frequencyToNote[i][0]+frequencyToNote[i+1][0]
                cleanNoteNames.append((totalTime, frequencyToNote[i][1]))
                frequencyToNote.remove(frequencyToNote[i+1]) #destructive!!!
            elif frequencyToNote[i][1]=="rest" and frequencyToNote[i+1][0]<(1.0*quarter)/4: #if theres a note that was cut off from rest, don't cut it off
                newTime=frequencyToNote[i][0]+frequencyToNote[i+1][0]
                cleanNoteNames.append((newTime, frequencyToNote[i][1]))
                frequencyToNote.remove(frequencyToNote[i+1])
            else:
                cleanNoteNames.append(frequencyToNote[i])
            i+=1
        cleanNoteNames.append(frequencyToNote[len(frequencyToNote)-1])
        return cleanNoteNames
    cleanNoteNames=cleanNoteNames(frequencyToNote, data)

    def noteLengthsMatchedtoNoteNames(cleanNoteNames, data):
        #matches note(letters) to note lengths (words) in a tuple
        bpm=data.bpm
        quarter=60.0/bpm
        notes=[] #list of tuples containing note name and note length (in words)
        for timePitchTuple in cleanNoteNames:
            time=timePitchTuple[0]
            noteType=""
            if time>=((1.0*quarter)/4) and time<((3.0*quarter)/4): #checks if eighth note
                noteType="eighth"
            elif time>=((3.0*quarter)/4) and time<(1.5*quarter): #checks if quarter note
                noteType="quarter"
            elif time>=(1.5*quarter) and time<(2.5*quarter): #checks if half note
                noteType="half"
            elif time>=(2.5*quarter) and time<(3.5*quarter): #checks if dotted Half
                noteType="dotted Half"
            elif time>=(3.5*quarter) and time<(4.5*quarter): #checks if whole note
                noteType="whole"
            if noteType!="":
                newTuple=(noteType, timePitchTuple[1])
                notes.append(newTuple)
        return notes
    notes=noteLengthsMatchedtoNoteNames(cleanNoteNames, data)
    data.notes=notes #final list containing tuples of note length (in words) and note name(in words) 

def getFrequenciesList(data):
    #gets frequencies from clean data.notes list to send to playback function
    frequencies=[]
    notesToFrequenciesDictionary=reverseDictionary(data.frequenciesToNotesDictionary)
    for note in data.notes:
        noteName=note[1]
        noteLength=note[0]
        frequency=notesToFrequenciesDictionary.get(noteName)
        if frequency==0:
            frequency=1
        if noteLength=="eighth":
            noteLength=0.5
        if noteLength=="quarter":
            noteLength=1
        if noteLength=="half":
            noteLength=2
        if noteLength=="dotted Half":
            noteLength=3
        if noteLength=="whole":
            noteLength=4
        frequencies.append((noteLength, frequency))
    data.cleanLengthsAndFrequencies=frequencies

def play (frequency, length):
    #taken from http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    def sine(frequency, length, rate):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        return numpy.sin(numpy.arange(length) * factor)

    def play_tone(stream, frequency=440, length=.5, rate=44100):
        chunks = []
        chunks.append(sine(frequency, length, rate))
        chunk = numpy.concatenate(chunks) * 0.25
        stream.write(chunk.astype(numpy.float32).tostring())

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)
    play_tone(stream, frequency, length)
    stream.close()
    p.terminate()

def playBack(data):
    #loops thorugh all the frequencies and calls play to get a continuous sound
    getFrequenciesList(data)
    for note in data.cleanLengthsAndFrequencies:
        length=((60*1.0)/data.bpm)*note[0]
        frequency=note[1]
        play(frequency, length)

##########################################################
def drawStartScreen(canvas, data, dx):
    if data.startScreen:
        canvas.create_rectangle(0,0,data.width,data.height, fill="azure")
        data.startRectanglex1=data.width//3
        data.startRectanglex2=data.width*2//3
        data.startRectangley1=data.height//5
        data.startRectangley2=data.height*2//3
        textSeparation=20
        canvas.create_rectangle(data.startRectanglex1, data.startRectangley1, data.startRectanglex2, data.startRectangley2, outline="aquamarine2", width=5)
        centerxRectangle=(data.width*2//3+data.width//3)//2
        centeryRectangle=(data.height*2//3+data.height//5)//2
        canvas.create_text(centerxRectangle, centeryRectangle, text="Click Here to Record", font="Arial 16")
        canvas.create_text(centerxRectangle, centeryRectangle+textSeparation, text="and Write Sheet Music!", font="Arial 16" )
        canvas.create_text(centerxRectangle, data.height//7, text="Write Notes", font="Arial 30 bold")
    
    def drawTrebleClefDecal(canvas, data, x ,y):
        #draws the moving treble clefs
        width=20
        sep=20
        topCirlceLeftX=x-width//2
        topCirlceLeftY=y-sep*2.5
        topCircleRightX=x+width//2
        topCircleRightY=y-sep*.5
        canvas.create_oval(topCirlceLeftX, topCirlceLeftY, topCircleRightX, topCircleRightY, width=3, outline="DarkGoldenRod1")
        lineLeftX=topCirlceLeftX+2
        lineLeftY=y-sep
        lineRightX=x+width*.5
        lineRightY=y+3.5*sep
        canvas.create_line(lineLeftX, lineLeftY, lineRightX, lineRightY, width=3, fill="DarkGoldenRod1")
        lineSegmentRightX=x
        lineSegmentRightY=y-sep*.5
        lineSegmentLeftX=x-width
        lineSegmentLeftY=y+.5*sep
        canvas.create_line(lineSegmentRightX, lineSegmentRightY, lineSegmentLeftX, lineSegmentLeftY, width=3, fill="DarkGoldenRod1")
        bigCircleLeftX=lineSegmentLeftX
        bigCircleLeftY=lineSegmentLeftY-sep*.5
        bigCircleRightX=x+width
        bigCircleRightY=y+2.5*sep
        canvas.create_arc(bigCircleLeftX, bigCircleLeftY, bigCircleRightX, bigCircleRightY, start=130, extent=240, style=ARC, width=3, outline="DarkGoldenRod1")
        smallCircleLeftX=x-width*.5
        smallCircleLeftY=y+.5*sep
        smallCircleRightX=x+width
        smallCircleRightY=y+2*sep
        canvas.create_arc(smallCircleLeftX, smallCircleLeftY, smallCircleRightX, smallCircleRightY, style=ARC, start=0, extent=240, width=3, outline="DarkGoldenRod1")
    for i in range(0+dx, 14+dx, 1): #draws multiple
        y=(data.height*7//8)+50*math.sin(i)
        x=(i*40+30)%900 #animates
        drawTrebleClefDecal(canvas, data, x, y)
    
def drawRecordButton(canvas, data):
    data.recordButtonCenterx=data.sideBarWidth//2
    data.recordButtonCentery=data.sideBarButtonsDistance*6
    data.recordButtonOuterRadius=data.sideBarWidth//8
    data.recordButtonInnerRadius=data.recordButtonOuterRadius*5//9
    #creates outer circle
    canvas.create_oval(data.recordButtonCenterx-data.recordButtonOuterRadius, 
        data.recordButtonCentery-data.recordButtonOuterRadius, 
        data.recordButtonCenterx+data.recordButtonOuterRadius, 
        data.recordButtonCentery+data.recordButtonOuterRadius, width=2)
    #creates inner red circle
    canvas.create_oval(data.recordButtonCenterx-data.recordButtonInnerRadius,
     data.recordButtonCentery-data.recordButtonInnerRadius, 
     data.recordButtonCenterx+data.recordButtonInnerRadius,
      data.recordButtonCentery+data.recordButtonInnerRadius, fill="red")
    textMargin=8
    canvas.create_text(data.recordButtonCenterx,
        data.recordButtonCentery+data.recordButtonOuterRadius+textMargin,
        text="Record")

def drawEighthRest(canvas, data):
    x, y=data.currDrawPosX-1.0*data.lineSeparation//2, data.currDrawPosY
    centerCirclePtX=x-1.0*data.noteWidth//2
    centerCirclePtY=y-1.0*data.noteHeight//2
    circleRadius=1.0*data.noteWidth//3
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_oval(centerCirclePtX-circleRadius, centerCirclePtY-circleRadius,
    centerCirclePtX+circleRadius, centerCirclePtY+circleRadius, fill="black")
    rightPtStemX=x+1.0*data.noteWidth//2
    rightPtStemY=centerCirclePtY-circleRadius
    canvas.create_line(centerCirclePtX, centerCirclePtY+circleRadius,
    rightPtStemX, rightPtStemY)
    leftPtStemX=x-1.0*data.noteWidth//2
    leftPtStemY=y+data.lineSeparation
    canvas.create_line(leftPtStemX, leftPtStemY, rightPtStemX, rightPtStemY)
    data.beatsDrawn+=.5
    data.currDrawPosX+=data.noteSeparationInMeasure*.4
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])

def drawQuarterRest(canvas, data):
    x, y =data.currDrawPosX, data.currDrawPosY
    firstStemLeftX=x-1.0*data.noteWidth//2
    firstStemLeftY=y-data.lineSeparation
    firstStemRightX=x+1.0*data.noteWidth//2
    firstStemRightY=y
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_line(firstStemLeftX, firstStemLeftY, firstStemRightX, firstStemRightY)
    secondStemLeftY=y+1.0*data.lineSeparation//2
    canvas.create_line(firstStemLeftX, secondStemLeftY, firstStemRightX, firstStemRightY, width=4)
    thirdStemRightX=x+1.0*data.noteWidth//2
    thirdStemRightY=y+data.lineSeparation
    canvas.create_line(firstStemLeftX, secondStemLeftY, thirdStemRightX, thirdStemRightY)
    roundPtLeftX=firstStemLeftX
    roundPtLeftY=y+data.lineSeparation
    roundPtRightX=thirdStemRightX
    roundPtRightY=y+2*data.lineSeparation
    canvas.create_arc(roundPtLeftX, roundPtLeftY, roundPtRightX, roundPtRightY, start=70, extent=220 , style=ARC, width=2)
    data.beatsDrawn+=1
    data.currDrawPosX+=data.noteSeparationInMeasure*.9
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])

def drawHalfRest(canvas, data):
    x, y=data.currDrawPosX, data.currDrawPosY
    leftX=x-data.noteWidth*3.0//4
    leftY=y
    rightX=x+data.noteWidth*3.0//4
    rightY=y+1.0*data.lineSeparation//2
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_rectangle(leftX, leftY, rightX, rightY, fill="black") #creates the box part
    canvas.create_line(leftX-1.0*data.noteWidth//4, rightY, rightX+1.0*data.noteWidth//4, rightY, width=2) #creates the line part
    data.beatsDrawn+=2
    data.currDrawPosX+=data.noteSeparationInMeasure*1.8
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound]) #need this as a place holder

def drawWholeRest(canvas, data):
    x,y=data.currDrawPosX, data.currDrawPosY
    leftX=x-data.noteWidth*3.0//4
    leftY=y-1.0*data.lineSeparation//2
    rightX=x+data.noteWidth*3.0//4
    rightY=y
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_rectangle(leftX, leftY, rightX, rightY, fill="black") #creates box part
    canvas.create_line(leftX-1.0*data.noteWidth//4, leftY, rightX+1.0*data.noteWidth//4, leftY, width=2) #creates line part
    data.beatsDrawn+=4
    data.noteSeparationInMeasure+=data.noteSeparationInMeasure*3.8
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])

def drawEighthNote(canvas, data, x, y):
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    #draw circle part
    canvas.create_oval(x-data.noteWidth, y-data.noteHeight, x+data.noteWidth, y+data.noteHeight, fill="black")
    #draw stem
    canvas.create_line(data.stemSide, y, data.stemSide, data.stemBottom)
    #draw Flag
    if data.stemBottom>y:
        canvas.create_line(data.stemSide, data.stemBottom, data.stemSide+data.dotDistance,data.stemBottom-data.stemHeight//2)
    else:   
        canvas.create_line(x+data.noteWidth, y-data.stemHeight, x+data.noteWidth+data.dotDistance,y-data.stemHeight//2)
    data.beatsDrawn+=.5
    data.currDrawPosX+=data.noteSeparationInMeasure*.4
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])


def drawDottedHalfNote(canvas, data ,x ,y):
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_oval(x-data.noteWidth, y-data.noteHeight, x+data.noteWidth, y+data.noteHeight)
    canvas.create_line(data.stemSide, y, data.stemSide, data.stemBottom)
    canvas.create_oval(x+data.noteWidth+data.dotDistance-data.dotRadius, 
        y-data.dotRadius, x+data.noteWidth+data.dotDistance+data.dotRadius, 
        y+data.dotRadius, fill="black") #draws dot
    data.beatsDrawn+=3
    data.currDrawPosX+=data.noteSeparationInMeasure*3
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound]) 

def drawWholeNote(canvas, data, x, y):
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_oval(x-data.noteWidth, 
        y-data.noteHeight, x+data.noteWidth,
         y+data.noteHeight, fill="black")
    canvas.create_oval(x-data.wholeNoteInsideShrink*data.noteWidth,
     y-data.noteHeight, x+data.wholeNoteInsideShrink*data.noteWidth, 
     y+data.noteHeight, fill="ghost white") #draws hole in middle
    data.beatsDrawn+=4
    data.currDrawPosX+=data.noteSeparationInMeasure*4
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])

def drawHalfNote(canvas, data, x, y):
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_oval(x-data.noteWidth, y-data.noteHeight, x+data.noteWidth, y+data.noteHeight)
    canvas.create_line(data.stemSide, y, data.stemSide, data.stemBottom)
    data.beatsDrawn+=2
    data.currDrawPosX+=data.noteSeparationInMeasure*2
    if data.drawFirstTime:
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])

def drawQuarterNote(canvas, data, x, y):
    leftBound=x-data.noteWidth
    topBound=y-data.noteHeight
    bottomBound=y+data.noteHeight
    rightBound=x+data.noteWidth
    canvas.create_oval(x-data.noteWidth, y-data.noteHeight, 
        x+data.noteWidth, y+data.noteHeight, fill="black")
    canvas.create_line(data.stemSide, y, data.stemSide, data.stemBottom)
    data.beatsDrawn+=1
    data.currDrawPosX+=data.noteSeparationInMeasure
    if data.drawFirstTime: #create a bounds list that keeps track of where notes are
    #allows for checking for click in keypressed
        data.noteBounds.append([leftBound, topBound, rightBound, bottomBound])

def drawExtraLine(canvas, data, y, numExtraLines, aboveOrBelowStaff, onOrOffLine):
    #checks if need lines above or below staff accordingly
    if onOrOffLine=="off" and aboveOrBelowStaff=="above":
        y+=data.noteHeight #line is below note
    if onOrOffLine=="off" and aboveOrBelowStaff=="below":
        y-=data.noteHeight #line is above note
    lineRadius=data.noteSeparationInMeasure//5
    for i in range(numExtraLines):
        canvas.create_line(data.currDrawPosX-lineRadius, y, data.currDrawPosX+lineRadius, y)
        if aboveOrBelowStaff=="above":
            y+=data.lineSeparation
        else:
            y-=data.lineSeparation
def stemDims(data, y, octaveUp, octaveDown, numNotesAwayFromC, noteName):
    #finds out what sides/direction stem should point
    notesToFrequencies=reverseDictionary(data.frequenciesToNotesDictionary)
    frequencyNote=notesToFrequencies.get(noteName)
    if data.clef=="bass":
        if frequencyNote>=notesToFrequencies.get("d"): #if above this, stem is on left
            stemSide=data.currDrawPosX-data.noteWidth
            stemBottom=y+data.stemHeight #points down
        else: #stem on right 
            stemSide=data.currDrawPosX+data.noteWidth
            stemBottom=y-data.stemHeight #points up
    else:
        if frequencyNote>=notesToFrequencies.get("c''"): #if above this stem on left
            stemSide=data.currDrawPosX-data.noteWidth
            stemBottom=y+data.stemHeight #points down
        else: #stem on right
            stemSide=data.currDrawPosX+data.noteWidth
            stemBottom=y-data.stemHeight#points up
    data.stemSide=stemSide
    data.stemBottom=stemBottom

def drawSharp(canvas, data, x, y):
    y+=2
    sharpWidth=2
    sharpHeight=6
    overHang=2
    vertLeft=x-sharpWidth
    vertLeftTop=y-data.lineSeparation
    vertLeftBottom=vertLeftTop+data.lineSeparation*2
    vertRight=x+sharpWidth
    vertRightTop=y-data.lineSeparation-overHang
    vertRightBottom=vertRightTop+data.lineSeparation*2
    canvas.create_line(vertLeft, vertLeftTop, vertLeft, vertLeftBottom, width=1)
    canvas.create_line(vertRight, vertRightTop, vertRight, vertRightBottom, width=1)
    horz1Left=x-sharpWidth-overHang
    horz1Right=x+sharpWidth+overHang
    horz1Bottom=y-.2*data.lineSeparation
    horz1Top=horz1Bottom-.5*data.lineSeparation
    canvas.create_line(horz1Left, horz1Bottom, horz1Right, horz1Top, width=1)
    horz2Left=horz1Left-overHang//2
    horz2Right=horz1Right-overHang//2
    horz2Top=horz1Top+sharpHeight
    horz2Bottom=horz1Bottom+sharpHeight
    canvas.create_line(horz2Left, horz2Bottom, horz2Right, horz2Top, width=1)

def checkNotes(data):
    measuresPerLine=4
    #if we've used up the whole line, start drawing on a new line
    if data.currDrawPosX>=data.sheetBorderRight-data.marginStaffFromSideBorder//2:
        data.currDrawPosX=data.sheetBorderLeft+data.marginStaffFromSideBorder+ data.noteSeparationInMeasure//2
        # lineNumber=(1.0*data.beatsDrawn//(measuresPerLine*data.timeSignature[0]))+1
        lineNumber= int(math.ceil(1.0*data.beatsDrawn//(measuresPerLine*data.timeSignature[0])))
        data.currDrawPosY=data.sheetBorderTop+data.marginStaffFromTopBorder+ 1.5*data.lineSeparation+2*data.staffSeparation*(lineNumber)
def drawNotes(canvas, data, notes):
    data.oneNoteSeparationDistance=data.lineSeparation//2
    for note in data.notes: #time note tuple
        checkNotes(data)
        noteLength, noteName=note
        if noteName!="rest":
            noteLetter=noteName[0]
            numNotesAwayFromC=(ord(noteLetter)-ord("c")) # if positive, note is above c
            if data.clef=="bass":
                numNotesAwayFromC-=2
            y=data.currDrawPosY-data.oneNoteSeparationDistance*numNotesAwayFromC
            octaveUp=noteName.count("'") #a "'" signifies an octave up
            octaveDown=noteName.count(",") #a"," signifies an octave down"
            #octave goes from c' d' e' f' g' a' b' so the next function makes sure it draws on staff accordingly
            if (numNotesAwayFromC<0 and data.clef=="treble") or (numNotesAwayFromC<-2 and data.clef=="bass"):
                if octaveUp!=0 or (octaveUp==0 and octaveDown==0):
                    octaveUp+=1 
                elif octaveDown!=0:
                    octaveDown-=1
            if data.clef=="treble": #notes are based in bass clef, so need to adjust
                octaveDown+=2
            octaveSeparation=7 #notes in an octave
            for i in range(octaveUp):
                y-=data.oneNoteSeparationDistance*octaveSeparation 
            for i in range(octaveDown):
                y+=data.oneNoteSeparationDistance*octaveSeparation
            stemDims(data, y, octaveUp, octaveDown, numNotesAwayFromC, noteName)
            distanceFromC=numNotesAwayFromC+octaveUp*octaveSeparation-octaveDown*octaveSeparation #distance from c in staff
            if abs(distanceFromC)%2==0:
                onOrOffLine="off" #based on distance from "c" note is it on or off line?
            if abs(distanceFromC)%2==1:
                onOrOffLine="on"
            if distanceFromC>4: #note Steps away from C above staff
                numExtraLines=int(math.ceil(1.0*(distanceFromC-4)/2))
                drawExtraLine(canvas, data, y, numExtraLines, "above", onOrOffLine)
            if distanceFromC<-6: #note steps away from c below staff
                numExtraLines=int(math.ceil((1.0*(abs(-6-distanceFromC)))/2)) 
                drawExtraLine(canvas, data, y, numExtraLines, "below", onOrOffLine)
            if "is" in noteName:
                x=data.currDrawPosX-2*data.noteWidth
                drawSharp(canvas, data, x, y)
            if noteLength=="quarter":
                drawQuarterNote(canvas, data, data.currDrawPosX, y) #need to pass in data.currDrawPosx because this changes as you edit
            if noteLength=="half":
                drawHalfNote(canvas, data, data.currDrawPosX, y)
            if noteLength=="dotted Half":
                drawDottedHalfNote(canvas, data, data.currDrawPosX, y)
            if noteLength=="whole":
                drawWholeNote(canvas, data, data.currDrawPosX, y)
            if noteLength=="eighth":
                drawEighthNote(canvas, data, data.currDrawPosX, y)
        else:
            if noteLength=="eighth":
                drawEighthRest(canvas, data)
            elif noteLength=="quarter":
                drawQuarterRest(canvas, data)
            elif noteLength=="half":
                drawHalfRest(canvas, data)
            elif noteLength=="whole":
                drawWholeRest(canvas, data)
        
        data.notesDrawn.append(note)
        y=0
    data.drawFirstTime=False 
    data.beatsDrawn=0
       
def drawBar(canvas, data, x, y):
    #draw individual bar
    left=data.sheetBorderLeft+data.marginStaffFromSideBorder+x
    top=data.sheetBorderTop+data.marginStaffFromTopBorder+y
    bottom=top+data.lineSeparation*4
    canvas.create_line(left, top, left, bottom)
    
def drawBarLines(canvas, data):
    #draws the set of bar lines
    x,y=0,0
    numBarLines=5
    for line in range(data.lines):
        for barLines in range(numBarLines):
            if barLines==0:
                x+=data.measureWidth
                continue
            drawBar(canvas, data, x, y)
            x+=data.measureWidth
        y+=data.lineSeparation*5+data.staffSeparation
        x=0

def drawLine(canvas, data, y):
    measuresPerLine=4.4
    startPtTop=data.sheetBorderTop+data.marginStaffFromTopBorder+y
    startPtLeft=data.sheetBorderLeft+data.marginStaffFromSideBorder//2
    startPtRight=startPtLeft+measuresPerLine*data.measureWidth
    canvas.create_line(startPtLeft-data.clefWidth, startPtTop, startPtRight, startPtTop)

def drawTrebleClef(canvas, data, y):
    x=data.currDrawPosX-2*data.clefWidth-data.clefWidth
    topCirlceLeftX=x-data.noteWidth//2
    topCirlceLeftY=y-data.lineSeparation*2.5
    topCircleRightX=x+data.noteWidth//2
    topCircleRightY=y-data.lineSeparation*.5
    canvas.create_oval(topCirlceLeftX, topCirlceLeftY, topCircleRightX, topCircleRightY, width=1.5)
    lineLeftX=topCirlceLeftX
    lineLeftY=y-data.lineSeparation
    lineRightX=x+data.noteWidth*.5
    lineRightY=y+3.5*data.lineSeparation
    canvas.create_line(lineLeftX, lineLeftY, lineRightX, lineRightY, width=1.5)
    lineSegmentRightX=x
    lineSegmentRightY=y-data.lineSeparation*.5
    lineSegmentLeftX=x-data.noteWidth
    lineSegmentLeftY=y+.5*data.lineSeparation
    canvas.create_line(lineSegmentRightX, lineSegmentRightY, lineSegmentLeftX, lineSegmentLeftY, width=1.5)
    bigCircleLeftX=lineSegmentLeftX
    bigCircleLeftY=lineSegmentLeftY-data.lineSeparation*.5
    bigCircleRightX=x+data.noteWidth
    bigCircleRightY=y+2.5*data.lineSeparation
    canvas.create_arc(bigCircleLeftX, bigCircleLeftY, bigCircleRightX, bigCircleRightY, start=130, extent=240, style=ARC, width=1.5)
    smallCircleLeftX=x-data.noteWidth*.5
    smallCircleLeftY=y+.5*data.lineSeparation
    smallCircleRightX=x+data.noteWidth
    smallCircleRightY=y+2*data.lineSeparation
    canvas.create_arc(smallCircleLeftX, smallCircleLeftY, smallCircleRightX, smallCircleRightY, style=ARC, start=0, extent=240, width=1.5)

def drawBassClef(canvas, data, y):
    x= data.currDrawPosX-3*data.clefWidth
    dotRadius=data.lineSeparation//3
    mainDotLeftX=x-1.5*data.noteWidth
    mainDotLeftY=y-data.lineSeparation*3//4
    mainDotRightX=mainDotLeftX+2*dotRadius
    mainDotRightY=mainDotLeftY+2*dotRadius
    canvas.create_oval(mainDotLeftX, mainDotLeftY, mainDotRightX, mainDotRightY, fill="black")
    arcLeftX=mainDotLeftX
    arcLeftY=mainDotLeftY-data.lineSeparation
    arcRightX=arcLeftX+3*data.noteWidth
    arcRightY=arcLeftY+2*data.lineSeparation
    canvas.create_arc(arcLeftX, arcLeftY , arcRightX , arcRightY, style=ARC, start=-30, extent=230, width=1.5)
    lineSegmentRightX=x+data.noteWidth*1.5
    lineSegmentRightY=y-dotRadius
    lineSegmentLeftX=x-data.noteWidth*2//3
    lineSegmentLeftY=y+1.5*data.lineSeparation
    canvas.create_line(lineSegmentRightX, lineSegmentRightY, lineSegmentLeftX, lineSegmentLeftY, width=1.5)
    smallDotRadius=dotRadius*2//3
    dot1LeftX=arcRightX+2*smallDotRadius
    dot1LeftY=y-data.lineSeparation-smallDotRadius
    dot1RightX=dot1LeftX+2*smallDotRadius
    dot1RightY=dot1LeftY+2*smallDotRadius
    canvas.create_oval(dot1LeftX, dot1LeftY, dot1RightX, dot1RightY, fill="black")
    dot2LeftX=dot1LeftX
    dot2LeftY=dot1LeftY+data.lineSeparation
    dot2RightX=dot1RightX
    dot2RightY=dot1RightY+data.lineSeparation
    canvas.create_oval(dot2LeftX, dot2LeftY, dot2RightX, dot2RightY, fill="black")

def drawClef(canvas, data, y):
    if data.clef=="treble":
        drawTrebleClef(canvas, data, y)
    if data.clef=="bass":
        drawBassClef(canvas, data, y)

def drawTimeSignature(canvas, data, y):
    midTopNumY=y-data.lineSeparation
    midTopNumX=data.currDrawPosX-2*data.clefWidth
    midBottomNumY=y+data.lineSeparation
    midBottomNumX=midTopNumX
    if data.timeSignature==(4,4):
        topNum="4"
    else:
        topNum="3"
    canvas.create_text(midTopNumX, midTopNumY, text=topNum, font="Times 25 bold")
    canvas.create_text(midBottomNumX, midBottomNumY, text="4", font="Times 25 bold")
def drawStaff(canvas, data):
    y=0
    linesPerStaff=5
    data.currDrawPosY=data.sheetBorderTop+data.marginStaffFromTopBorder+ 1.5*data.lineSeparation #y coordinate of middle C (treble clef)
    for line in range(data.lines):
        for line in range(linesPerStaff):
            drawLine(canvas, data, y)
            y+=data.lineSeparation
        y+=data.staffSeparation
        drawClef(canvas, data, y+data.lineSeparation*2.5)
        drawBPM(canvas, data)  
        drawTimeSignature(canvas, data, y+data.lineSeparation*2.5)  
    drawBarLines(canvas, data)

def getMeasuresAndLines(data):
    measuresPerLine=4
    beats=0
    for note in data.notes:
        noteLength=note[0]
        if noteLength=="quarter":
            beats+=1
        if noteLength=="half":
            beats+=2
        if noteLength=="dotted Half":
            beats+=3
        if noteLength=="whole":
            beats+=4
        if noteLength=="eighth":
            beats+=.5
    data.totalBeats=beats
    data.measures=math.ceil(beats/data.timeSignature[0])
    data.lines=int(math.ceil(1.0*data.measures/measuresPerLine))
    

def drawTitle(canvas, data):
    midX=data.sheetBorderLeft+(data.sheetBorderRight-data.sheetBorderLeft)//2
    midY=data.sheetBorderTop+data.marginStaffFromTopBorder//2
    canvas.create_text(midX, midY, text=data.sheetMusicTitle, font="Times 24 bold")

def drawBPM(canvas, data):
    x=data.currDrawPosX-3*data.clefWidth
    y=data.currDrawPosY-5*data.lineSeparation
    canvas.create_oval(x-data.noteWidth, y-data.noteHeight, 
        x+data.noteWidth, y+data.noteHeight, fill="black")
    canvas.create_line(x+data.noteWidth, y, x+data.noteWidth, y-data.stemHeight)
    textX=x+data.measureWidth//5
    textY=y
    text="= "+ str(data.bpm)
    canvas.create_text(textX, textY, text=text, font="Times 15 bold")

def drawSheetMusic(canvas, data, notes):
    getMeasuresAndLines(data)
    drawStaff(canvas, data)
    drawNotes(canvas, data, notes)
    drawTitle(canvas, data)
    
def drawQuarterNoteInButton(canvas, data,x,y):
    noteHeight=data.recordButtonOuterRadius//3
    stemHeight=data.recordButtonOuterRadius
    noteWidth=data.recordButtonOuterRadius//3
    canvas.create_oval(x-noteWidth, y-noteHeight, 
        x+noteWidth, y+noteHeight, fill="black")
    canvas.create_line(x+noteWidth, y, 
        x+noteWidth, y-stemHeight)

def drawCreateSheetMusicButton(canvas, data):
    data.musicButtonCenterx=data.sideBarWidth//2
    data.musicButtonCentery=data.sideBarButtonsDistance*7
    data.musicButtonOuterRadius=data.sideBarWidth//8
    canvas.create_oval(data.musicButtonCenterx-data.musicButtonOuterRadius, 
        data.musicButtonCentery-data.musicButtonOuterRadius, 
        data.musicButtonCenterx+data.musicButtonOuterRadius, 
        data.musicButtonCentery+data.musicButtonOuterRadius, width=2)
    drawQuarterNoteInButton(canvas, data, data.musicButtonCenterx, 
        data.musicButtonCentery+data.recordButtonInnerRadius//2)
    textMargin=8
    canvas.create_text(data.musicButtonCenterx,
        data.musicButtonCentery+data.musicButtonOuterRadius+textMargin,
        text="Sheet Music")

def drawSaveButton(canvas, data):
    data.saveButtonWidth=data.sideBarWidth//2
    data.saveButtonHeight=data.height//30
    data.saveButtonLeft=data.sideBarWidth//4
    data.saveButtonTop=data.height-data.sideBarButtonsDistance
    data.saveButtonRight=data.saveButtonLeft+data.saveButtonWidth
    data.saveButtonBottom=data.saveButtonTop+data.saveButtonHeight
    canvas.create_rectangle(data.saveButtonLeft, data.saveButtonTop, data.saveButtonRight, data.saveButtonBottom, outline="tomato2", width=2)
    canvas.create_text(data.saveButtonLeft+data.saveButtonWidth//2, data.saveButtonTop+data.saveButtonHeight//2, text="Save")

def drawClefOptions(canvas, data):
    canvas.create_text(data.sideBarWidth//2, data.sideBarButtonsDistance, text="Pick clef:", font="Arial 15")
    data.trebleBoxLeft=data.sideBarWidth//15
    data.trebleBoxTop=data.sideBarButtonsDistance*3//2 - 3*data.lineSeparation//2
    data.trebleBoxRight=data.sideBarWidth//2-data.trebleBoxLeft
    data.trebleBoxBottom=data.trebleBoxTop+3*data.lineSeparation
    canvas.create_text(data.sideBarWidth//4, data.sideBarButtonsDistance*3//2, text="treble", font="Arial 15")
    trebleColor="black"
    if data.trebleSelected:
        trebleColor="DodgerBlue2" 
    canvas.create_rectangle(data.trebleBoxLeft, data.trebleBoxTop,
     data.trebleBoxRight, data.trebleBoxBottom, outline=trebleColor, width=2)
    data.bassBoxLeft=data.sideBarWidth//2+data.trebleBoxLeft
    data.bassBoxTop=data.trebleBoxTop
    data.bassBoxRight=data.sideBarWidth-data.trebleBoxLeft
    data.bassBoxBottom=data.trebleBoxBottom
    canvas.create_text(data.sideBarWidth*3//4, data.sideBarButtonsDistance*3//2, text="bass")
    bassColor="black"
    if data.bassSelected:
        bassColor="DodgerBlue2"
    canvas.create_rectangle(data.bassBoxLeft, data.bassBoxTop, data.bassBoxRight, data.bassBoxBottom, 
        outline=bassColor, width=2)

def drawTimeSignatureOptions(canvas, data):
    #box 1 is (4,4)
    #box 2 is (3,4)
    boxWidth=data.sideBarWidth//3
    boxHeight=data.sideBarButtonsDistance//2
    canvas.create_text( data.sideBarWidth//2,data.trebleBoxBottom+data.sideBarButtonsDistance*3//4, text="Pick time signature:", font= "Arial 15")
    data.timeSigBox1Left=data.sideBarWidth//15
    data.timeSigBox1Right=data.timeSigBox1Left+boxWidth
    data.timeSigBox1Top=data.trebleBoxBottom+data.sideBarButtonsDistance
    data.timeSigBox1Bottom=data.timeSigBox1Top+boxHeight
    firstNumY=data.timeSigBox1Top+boxHeight//4
    secondNumY=data.timeSigBox1Bottom-boxHeight//4
    box1NumX=data.timeSigBox1Left+boxWidth//2
    data.timeSigBox2Left=data.sideBarWidth//2+data.timeSigBox1Left
    data.timeSigBox2Right=data.timeSigBox2Left+boxWidth
    data.timeSigBox2Top=data.timeSigBox1Top
    data.timeSigBox2Bottom=data.timeSigBox1Bottom
    box2NumX=data.timeSigBox2Left+boxWidth//2
    color44="black"
    if data.timeSignature==(4,4):
        color44="DodgerBlue2"
    canvas.create_rectangle(data.timeSigBox1Left, data.timeSigBox1Top, data.timeSigBox1Right, data.timeSigBox1Bottom, width=2, outline=color44)
    canvas.create_text(box1NumX, firstNumY, text="4", font="Times 14 bold")
    canvas.create_text(box1NumX, secondNumY,text="4", font="Times 14 bold")
    color34="black"
    if data.timeSignature==(3,4):
        color34="DodgerBlue2"
    canvas.create_rectangle(data.timeSigBox2Left,data.timeSigBox2Top,data.timeSigBox2Right,data.timeSigBox2Bottom, width=2, outline=color34)
    canvas.create_text(box2NumX, firstNumY, text="3", font="Times 14 bold")
    canvas.create_text(box2NumX, secondNumY, text="4", font="Times 14 bold")


def draw5SecBox(canvas, data, boxWidth, boxHeight):
    data.sec5BoxLeft=data.sideBarWidth//6
    data.sec5BoxRight=data.sec5BoxLeft+boxWidth
    data.sec5BoxTop=data.timeSigBox2Bottom+data.sideBarButtonsDistance
    data.sec5BoxBottom=data.sec5BoxTop+boxHeight
    color="black"
    if data.recordSeconds==5:
        color="DodgerBlue2"
    canvas.create_rectangle(data.sec5BoxLeft, data.sec5BoxTop, data.sec5BoxRight, data.sec5BoxBottom, outline=color, width=2)
    midTextX=data.sec5BoxLeft+boxWidth//2
    midTextY=data.sec5BoxTop+boxHeight//2
    canvas.create_text(midTextX, midTextY, text="5", font="Times 13")

def draw10SecBox(canvas, data, boxWidth, boxHeight):
    data.sec10BoxLeft=data.sec5BoxRight+boxWidth//2
    data.sec10BoxRight=data.sec10BoxLeft+boxWidth
    data.sec10BoxTop=data.timeSigBox2Bottom+data.sideBarButtonsDistance
    data.sec10BoxBottom=data.sec10BoxTop+boxHeight
    color="black"
    if data.recordSeconds==10:
        color="DodgerBlue2"
    canvas.create_rectangle(data.sec10BoxLeft, data.sec10BoxTop, data.sec10BoxRight, data.sec10BoxBottom, outline=color, width=2)
    midTextX=data.sec10BoxLeft+boxWidth//2
    midTextY=data.sec10BoxTop+boxHeight//2
    canvas.create_text(midTextX, midTextY, text="10", font="Times 13")

def draw20SecBox(canvas, data, boxWidth, boxHeight):
    data.sec20BoxLeft=data.sec5BoxLeft
    data.sec20BoxRight=data.sec20BoxLeft+boxWidth
    data.sec20BoxTop=data.sec10BoxBottom+boxHeight//2
    data.sec20BoxBottom=data.sec20BoxTop+boxHeight
    color="black"
    if data.recordSeconds==20:
        color="DodgerBlue2"
    canvas.create_rectangle(data.sec20BoxLeft, data.sec20BoxTop, data.sec20BoxRight, data.sec20BoxBottom, outline=color, width=2)
    midTextX=data.sec20BoxLeft+boxWidth//2
    midTextY=data.sec20BoxTop+boxHeight//2
    canvas.create_text(midTextX, midTextY, text="20", font="Times 13")

def draw30SecBox(canvas, data, boxWidth, boxHeight):
    data.sec30BoxLeft=data.sec10BoxLeft
    data.sec30BoxRight=data.sec30BoxLeft+boxWidth
    data.sec30BoxTop=data.sec10BoxBottom+boxHeight//2
    data.sec30BoxBottom=data.sec30BoxTop+boxHeight
    color="black"
    if data.recordSeconds==30:
        color="DodgerBlue2"
    canvas.create_rectangle(data.sec30BoxLeft, data.sec30BoxTop, data.sec30BoxRight, data.sec30BoxBottom, outline=color, width=2)
    midTextX=data.sec30BoxLeft+boxWidth//2
    midTextY=data.sec30BoxTop+boxHeight//2
    canvas.create_text(midTextX, midTextY, text="30", font="Times 13")

def drawPlayButton(canvas, data):
    data.playButtonCenterY=data.musicButtonCentery+data.musicButtonOuterRadius+data.sideBarButtonsDistance
    data.playButtonCenterX=data.sideBarWidth//2
    data.playButtonRadius=data.musicButtonOuterRadius
    data.playButtonLeft=data.playButtonCenterX-data.playButtonRadius
    data.playButtonRight=data.playButtonCenterX+data.playButtonRadius
    data.playButtonTop=data.playButtonCenterY-data.playButtonRadius
    data.playButtonBottom=data.playButtonCenterY+data.playButtonRadius
    canvas.create_oval(data.playButtonLeft, data.playButtonTop, data.playButtonRight, data.playButtonBottom)
    trianglePt1=(data.playButtonCenterX-data.playButtonRadius*2//3, data.playButtonCenterY-data.playButtonRadius*2//3)
    trianglePt2=(data.playButtonCenterX-data.playButtonRadius*2//3, data.playButtonCenterY+data.playButtonRadius*2//3)
    trianglePt3=(data.playButtonCenterX+data.playButtonRadius*2//3, data.playButtonCenterY)
    canvas.create_polygon(trianglePt1, trianglePt2, trianglePt3, fill="sienna2")
    textMargin=8
    textMidX=data.sideBarWidth//2
    textMidY=data.playButtonCenterY+data.playButtonRadius+textMargin
    canvas.create_text(textMidX, textMidY, text="Play")

def drawRecordSeconds(canvas, data):
    boxWidth, boxHeight= data.sideBarWidth//4, data.sideBarWidth//4
    canvas.create_text(data.sideBarWidth//2, data.timeSigBox2Bottom+data.sideBarButtonsDistance*3//4, text="Pick record seconds:", font="Arial 13")
    draw5SecBox(canvas, data, boxWidth, boxHeight) 
    draw10SecBox(canvas, data, boxWidth, boxHeight)
    draw20SecBox(canvas, data, boxWidth, boxHeight)
    draw30SecBox(canvas, data, boxWidth, boxHeight)

def drawRecordScreen(canvas, data):
    if data.recordScreen or data.helpScreen:
        color="ghost white"
        if data.helpScreen:
            color="peach puff"
        canvas.create_rectangle(0,0, data.width, data.height, fill=color)
        canvas.create_rectangle(0, 0, data.sideBarWidth, data.height, outline="IndianRed1", width=4)
        drawClefOptions(canvas, data)
        drawRecordButton(canvas, data)
        drawCreateSheetMusicButton(canvas, data)
        canvas.create_rectangle(data.sheetBorderLeft, data.sheetBorderTop, data.sheetBorderRight, data.sheetBorderBottom)
        # drawSaveButton(canvas, data)
        drawTimeSignatureOptions(canvas, data)
        drawRecordSeconds(canvas, data)
        drawPlayButton(canvas, data)
        if data.recordScreen and not data.helpScreen:
            drawBackButton(canvas, data)

def drawErrorMessageRecordFirst(canvas, data):
    #edited slightly from tkinter manual
    top = Toplevel()
    top.title("Error")
    msg = Message(top, text="Don't forget to record something first and enter a title before analyzing music!")
    msg.pack()
    button = Button(top, text="Dismiss", command=top.destroy)
    button.pack()
    data.errorMessageRecordFirst=False

def drawErrorMessagePickFirst(canvas, data):
    #edited from tkinter manual
    top = Toplevel()
    top.title("Error")
    msg = Message(top, text="Don't forget to select a clef, time signature, and record seconds before recording audio!")
    msg.pack()
    button = Button(top, text="Dismiss", command=top.destroy)
    button.pack()
    data.errorMessagePickFirst=False


def drawHelpScreen(canvas, data):
    drawRecordScreen(canvas, data)
    arrowDistance=data.width//8
    arrow="<<<<<<"
    arrowFont="Arial 20 bold"
    textFont="Arial 16"
    arrowX=data.recordButtonCenterx+arrowDistance
    textNextToArrow=arrowX+40
    center=data.sheetBorderLeft+(data.sheetBorderRight-data.sheetBorderLeft)//2
    canvas.create_text(center, 4*data.sheetBorderTop, text="Help Screen", font="Arial 25 bold")
    # canvas.create_text(center, 7*data.sheetBorderTop, text="Welcome to Write Notes! This is a program where users can record audio and instantaneously convert it to sheet music!", font="Arial 12")
    canvas.create_text(center, 7*data.sheetBorderTop, text="The program is simple to use! Just go down the side bar \n in order and see the music appear in front of your eyes!", font="Arial 15")
    
    alignClef=data.trebleBoxTop+(data.trebleBoxBottom-data.trebleBoxTop)//2
    clefText="Use this button to pick which clef you will record your audio in. \n You can also toggle this option after the sheet music is created"
    canvas.create_text(arrowX, alignClef, text=arrow, font=arrowFont)
    canvas.create_text(textNextToArrow, alignClef, text=clefText, font=textFont, anchor=W)
    

    alignTimeSig=data.timeSigBox1Top + (data.timeSigBox1Bottom-data.timeSigBox1Top)//2
    timeSigText="Use this button to pick which time signature you will record your music in. \n You can also toggle this option once the sheet music is generated"
    canvas.create_text(arrowX, alignTimeSig, text=arrow, font=arrowFont)
    canvas.create_text(textNextToArrow, alignTimeSig, text=timeSigText, font=textFont, anchor=W)
    
    alignRecordSec=data.sec5BoxBottom+(data.sec20BoxTop-data.sec5BoxBottom)//2
    recordSecText="Use this button to specify how long you want to record audio for"
    canvas.create_text(arrowX, alignRecordSec, text=arrow, font=arrowFont)
    canvas.create_text(textNextToArrow, alignRecordSec, text=recordSecText, font=textFont, anchor=W)


    alignRecordButton=data.recordButtonCentery
    recordButtonText="Click this button once you have specified all the options above. \n Once clicked, this button will bring up a popup screen where you will be \n prompted to enter a title for your piece. Afterwards, you can click record \n on that screen which will start the recording time"
    canvas.create_text(arrowX, alignRecordButton, text=arrow, font=arrowFont)
    canvas.create_text(textNextToArrow, alignRecordButton, text=recordButtonText, font=textFont, anchor=W)

    alignMusicButton=data.musicButtonCentery
    musicButtonText="Once you have recorded something, click this button to see your \n audio converted into sheet music"
    canvas.create_text(arrowX, alignMusicButton, text=arrow, font=arrowFont)
    canvas.create_text(textNextToArrow, alignMusicButton, text=musicButtonText, font=textFont, anchor=W)

    editFeaturex=data.sideBarWidth//2
    editFeaturey=data.musicButtonCentery+data.sideBarButtonsDistance*2//3
    canvas.create_text(editFeaturex, editFeaturey, text="Edit Feature!", font="Arial 16", fill="purple1")
    canvas.create_text(arrowX, editFeaturey, text=arrow, font=arrowFont)
    editText="This is a special feature you can use once your sheet music has been generated. \n Simply click on a note and use the up and down arrow keys to \n edit it and change the pitch"
    canvas.create_text(textNextToArrow, editFeaturey, text=editText, font=textFont, anchor=W)

    alignPlayback=data.playButtonBottom+(data.playButtonTop-data.playButtonTop)//2
    playbackText="Once your sheet music has been generated, click this button to hear the \n sheet music played back to you. The playback will reflect the \n notes on the page, so after editing, your new notes will be played back"
    canvas.create_text(arrowX, alignPlayback, text=arrow, font=arrowFont)
    canvas.create_text(textNextToArrow, alignPlayback, text=playbackText, font=textFont, anchor=W)
    
def drawHelpButton(canvas, data):
    helpButtonWidth=20
    helpButtonHeight=20
    data.helpButtonLeft=data.width//40
    data.helpButtonRight=data.helpButtonLeft+helpButtonWidth
    data.helpButtonTop=data.height//40
    data.helpButtonBottom=data.helpButtonTop+helpButtonHeight
    canvas.create_oval(data.helpButtonLeft, data.helpButtonTop, data.helpButtonRight, data.helpButtonBottom, outline="IndianRed1", width=2)
    textX=data.helpButtonLeft+((data.helpButtonRight-data.helpButtonLeft)//2)
    textY=data.helpButtonTop+((data.helpButtonBottom-data.helpButtonTop)//2)
    canvas.create_text(textX, textY, text="i", font="Arial 15 bold", fill="IndianRed1")

def drawBackButton(canvas, data):
    buttonHeight=20
    buttonWidth=20
    data.backButtonTop=data.playButtonBottom+data.sideBarButtonsDistance
    data.backButtonBottom=data.backButtonTop+buttonHeight
    data.backButtonLeft=data.helpButtonLeft
    data.backButtonRight=data.backButtonLeft+buttonWidth
    canvas.create_oval(data.backButtonLeft, data.backButtonTop, data.backButtonRight, data.backButtonBottom, width=2, outline="aquamarine4")
    textMidX=data.backButtonLeft+(data.backButtonRight-data.backButtonLeft)//2
    textMidY=data.backButtonTop+(data.backButtonBottom-data.backButtonTop)//2
    canvas.create_text(textMidX, textMidY, text="<", font="Arial 20 bold", fill="aquamarine4")

def redrawAll(canvas, data):
    data.dx+=1
    drawStartScreen(canvas, data, data.dx)
    drawRecordScreen(canvas, data)
    drawHelpButton(canvas, data)
    if data.showMusicScreen:
        data.currDrawPosX=data.sheetBorderLeft+data.marginStaffFromSideBorder+ data.noteSeparationInMeasure//2
        drawSheetMusic(canvas, data, data.notes) #need to include data.notes becuase notes change in save function
    if data.recordWindow:
        recordWindow(canvas, data)
    if data.errorMessageRecordFirst:
        drawErrorMessageRecordFirst(canvas, data)
    if data.errorMessagePickFirst:
        drawErrorMessagePickFirst(canvas, data)
    if data.helpScreen:
        drawHelpScreen(canvas, data)
    drawHelpButton(canvas, data) #keep this at the bottom of the function so its always visible
    
###################################
#taken from 15-112 course website
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800,800)