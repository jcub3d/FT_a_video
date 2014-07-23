'''
fft_a_video.py

Send a movie to k-space (sort of).

Tested on limited number of videos.  Some encodings don't play nice at the moment.

jcub3d
July 9, 2014
v. 1.0

Tested with: 
numpy 1.8.1
OpenCV 2.4.9
Ubuntu 14.04
Python 2.7.6
ffmpeg 2.2.git-d3e51b4

#Installing OpenCV: http://www.sysads.co.uk/2014/05/install-opencv-2-4-9-ubuntu-14-04-13-10/
'''

import numpy as np
import cv2
import cv2.cv as cv
import os, time


def main():
    #Options
    SHOW          = True # Watch vids as program runs (slows down processing a bit)
    COLOR         = True # False is grayscale
    NORMALL       = True # Normalize after every ft calc performed.  Wacky results.
    PROCESS_AUDIO = True # Reqires ffmpeg
    TIMES_TO_FT   = 4    #FT performed four times should result in the original image
                         #HOWEVER, as a frame is not time domain data, an ft of it is sort
                         #of meaningless 
                         # 1 or 3 (or odd numbers) is (sort of) kspace.  Not visually exciting. 

    filename = "test.flv"
    outName = "output.avi"
    fourcc = cv.CV_FOURCC(*'XVID') #encoding



    #Open video file to read and get some properties
    cap, fps, width, height, totalframes = initialize_input(filename)
    #Output file to write to
    out = cv2.VideoWriter(outName,fourcc, fps, (width,height))


    while(cap.isOpened()):   
        nextFrameExists, frame = cap.read()       
        if nextFrameExists:

            if COLOR:
                ftFrame = frame
                for number in range(TIMES_TO_FT):       #xrange would be better, but eliminated in Py3 
                    ftFrame = ftcolor(ftFrame,NORMALL)
                if not NORMALL:
                    ftFrame = normalize(ftFrame)
            else:
                #Frame to grayscale
                ftFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if NORMALL:    
                    for number in range(TIMES_TO_FT):                
                        ftFrame = ftnorm(ftFrame)  
                else:
                    for number in range(TIMES_TO_FT):                
                        ftFrame = ft(ftFrame)                        
                    ftFrame = normalize(ftFrame)

            if SHOW: 
                cv2.imshow('ft',ftFrame)
                cv2.imshow('orig',frame)

            #Write output video
            out.write(ftFrame)

            #Track progress
            print ("%.2f" % (cap.get(cv.CV_CAP_PROP_POS_FRAMES) / totalframes * 100)), "% complete \r",

            #Need this to watch vids
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            print "Finished transforming video.  Will now process audio..."
            cap.release()

    if PROCESS_AUDIO:
        #Strip audio from original file
        cmd = "ffmpeg -i %s -vn -ac 2 -ar 44100 -ab 320k -f mp3 output.mp3" % filename
        os.system(cmd)

        #Attach audio to transformed video
        cmd = "ffmpeg -i %s -i output.mp3 -map 0 -map 1 -codec copy -shortest final.avi" % outName
        os.system(cmd)

        #Delete temporary files
        cmd = "rm output.mp3 %s" % outName
        os.system(cmd)




def ft(ftFrame):
    return np.real(np.fft.fft2(ftFrame))  

def ift(ftFrame):
    return np.real(np.fft.ifft2(ftFrame))

def normalize(ftFrame):
    #ftFrame = np.nan_to_num(ftFrame) #Slows it down, but safer to do this
    ftFrame *= np.absolute( (255.0/ftFrame.max()) ) #Normalize to 0-255 after ft
    return ftFrame.astype(np.uint8) #Dtype needed by opencv

def ftnorm(ftFrame):
    ''' Crazy if applied multiple times '''
    ftFrame = ft(ftFrame)
    return normalize(ftFrame)

def ftcolor(frame,norm=True):
    fx,fy,fz = frame.shape
    frame = np.reshape(frame,(fx,fy*fz))
    if norm:
        frame = ftnorm(frame)
    else:
        frame = ft(frame)
    frame = np.reshape(frame,(fx,fy,fz))
    return frame

def initialize_input(filename):
    cap = cv2.VideoCapture(filename)
    try:
        fps = int(round( cap.get(cv.CV_CAP_PROP_FPS) ))
    except:
        fps = 24
        print "Could not identify framerate.  The program will probably crash."
    width  = int(round( cap.get(cv.CV_CAP_PROP_FRAME_WIDTH) ))
    height = int(round( cap.get(cv.CV_CAP_PROP_FRAME_HEIGHT) ))
    totalframes = cap.get(cv.CV_CAP_PROP_FRAME_COUNT)

    return cap, fps, width, height, totalframes



if __name__ == '__main__':
    main()
