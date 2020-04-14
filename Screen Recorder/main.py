import cv2
import numpy as np
import pyautogui
import winsound, time
import desktopmagic.screengrab_win32
import monitor_detect
from pynput import keyboard as kb
from threading import Thread
from win32gui import GetCursorPos as cursor
from PIL import Image




# define the codec
CODEC_AVI  = ("avi" , "XVID")
CODEC_MP4  = ("mp4" , "H264")
CODEC_DivX = ("divx", "DivX")
useCodec = CODEC_AVI # You may choose the codec you like to use


# Buffer about writing images to file. 
# Buffer: 0-> No Buffer, 1-> Buffering in array/list, 2-> Buffering in thread,
# Buffer: 3-> Hybrid between 1 and 2
BUFFER = 2
"""
Tips for the buffer mode.

It's very not recommended to disable the buffer mode, except you have a quantum computer
or supercomputer, or, if you want to set the fps to 1 or lesser. Because it'll be very
slow and significantly drop your fps.

It's a little bit not recommended to use buffer mode 1, except you want to record a
less-than-one minute video and have quite big memory/RAM. Because this mode consume
very much RAM/memory. However maintain the fps very very well (unless you're running out
of memory, which can be worse than other buffer mode in maintaining fps).

It's recommended to use either mode 2 or 3 because they're more stable in both memory and
time/fps.
The mode 2 always increased in memory, but it's very small. I think recording 1 day video will
not enough to have your memory/RAM full. However it's limited in time,
even if it's one-year-long.
However if your cpu and harddisk is not fast enough, the fps will be dropped. Unlike mode 3
which will try it's best to use memory approach to maintain the fps when the cpu is not
fast enough.

The mode 3, sometimes have bigger memory than mode 2, or mostly nearly same as mode 2 in memory.
Mode 3 also offer the speed/fps like mode 1 and 2. Mode 3 also won't always increased in
memory, as long as your cpu and harddisk is fast enough to write to the video file. So,
mostly, this mode can offer you an unlimited time. However if your cpu and harddisk can't
race with the captured images, it will increase in memory, but will do better than mode 2
to not drop the fps.
"""


SHOW_CURSOR = True

# First item is FPS when running on 1 monitor, and the second for 2 monitors.
# Please note that when recording on 2 monitors, fps will be dropped.
FPS = (7.0, 7.0) 
# Becareful, if your result video is all just one same picture, no movements, it means
# that you set the fps too big













MONITOR_COUNT = len(monitor_detect.enum_display_monitors())

if   (MONITOR_COUNT == 1):
    PLUS_EXTERNAL_MONITOR = False
    FPS = FPS[0]
elif (MONITOR_COUNT == 2):
    #Only support left-right monitor, not up-down. And the main monitor must be in the right
    #side of you.
    PLUS_EXTERNAL_MONITOR = True
    FPS = FPS[1]
else:
    raise Exception("Only support one or two monitor")


def beeping(): #To notify that the video record is going to be started
    for i in range(3):
        winsound.Beep(700 + i * 100, 150) # Beeping for frequency x*i + 700, for 150 ms


SCREEN_SIZE = list(pyautogui.size())


if (PLUS_EXTERNAL_MONITOR):
    SCREEN_SIZE[0] = (SCREEN_SIZE[0]*2)

SCREEN_SIZE = tuple(SCREEN_SIZE)

ENDED = False

SLOWDOWN = 1/FPS/4 #slowdown as much as 1/4 frames

def on_keypress(key):
    if (key == kb.Key.esc):

        print("escape pressed! Bye!")

        global ENDED
        ENDED = True
        
        return False
    
def eventHandler():
    listener = kb.Listener(on_press=on_keypress)
    listener.start()
    listener.join() # wait till listener will stop

def WriteOut(data):
    out, img = data
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    out.write(frame)
    
def Buffer3():
    while True:
        if ( len(buffer) ): #If there is any frame in buffer need to be decoded
            WriteOut((out, buffer.pop(0)))
        else:
            time.sleep(SLOWDOWN)

def main():
    global fourcc, FPS, out, thread, img, buffer

    fourcc = cv2.VideoWriter_fourcc(  *(useCodec[1])  )
    tmp = 'please enter file name\n' #Temporary
    out = cv2.VideoWriter(f"{input(tmp)}.{useCodec[0]}",
                          fourcc, FPS, tuple(SCREEN_SIZE))
    thread__ = Thread( target = eventHandler).start() # Handle escape key
    del tmp
    
    time.sleep(2)       # Get ready for recording
    beeping()             # Notify the user, "It's going to be recorded"
    time.sleep(0.1)     # A little bit pause

    if (SHOW_CURSOR):
        CursorImage = Image.open("cursor.png") # Load cursor image for being paste
        CursorImage = CursorImage.resize((32,32))

    Time = time.time()
    if   (BUFFER == 2):
        thread = []
    elif (BUFFER == 1):
        buffer = []
    elif (BUFFER == 3): 
        buffer = []    #wanna DRY but will make code a bit complicated, so I just WET
        thread = Thread(target = Buffer3)
        thread.start()
    
    
    try:
        while True:
            
            Time = Time + 1/FPS 
            
            # make a screenshot
            if (not PLUS_EXTERNAL_MONITOR):
                img = pyautogui.screenshot()
                if (SHOW_CURSOR):
                    img.paste(CursorImage, cursor(), CursorImage)
            else:
                # make a screenshot of multiple monitor
                img = desktopmagic.screengrab_win32.getScreenAsImage()
                if (SHOW_CURSOR):
                    x, y = cursor()
                    x = SCREEN_SIZE[0]//2 + x
                    img.paste(CursorImage, (x,y), CursorImage)
            
            if   (BUFFER == 0):
                WriteOut((out,img))
            elif (BUFFER == 1 or BUFFER == 3):
                buffer.append(img)
            elif (BUFFER == 2):
                thread.append( Thread(target = WriteOut, args = [(out, img)]) )
                thread[-1].start()

            if ENDED:
                print('legally stopped')
                break

            TooSlowFPS = False

            while (time.time() + .1 > Time and not ENDED): #accelerate
                #maintain the FPS stable if the machine is too slow (0.1 second slower)
                if (BUFFER == 2):
                    thread.append( Thread(target = WriteOut, args = [(out, img)]) )
                    thread[-1].start()
                elif (BUFFER == 1 or BUFFER == 3):
                    buffer.append(img)
                elif (BUFFER == 0):
                    WriteOut((out,img))
                Time = time.time() + 1/FPS
                TooSlowFPS = True
                print(".",end = "")
                
            while (time.time() + .3 < Time and not TooSlowFPS and not ENDED): #slow down
                # maintain the FPS stable if the machine is too fast (0.3 second faster)
                # "and not TooSlowFPS" prevent slow down after it's accelerated
                time.sleep(SLOWDOWN)
                print("-",end = "")
                
            
    except KeyboardInterrupt:
        pass
    finally:
        if   (BUFFER == 2):
            print("joining threads")
            while( len(thread) ):
                thread.pop(0).join()#Releasing abundant memory one by one
                
        elif (BUFFER == 1):
            print("writing files")
            while( len(buffer) ):
                WriteOut((out, buffer.pop(0) )) #Releasing abundant memory one by one
                
        # make sure everything is closed when exited
        cv2.destroyAllWindows()
        out.release()
        print("Released")


if __name__ == "__main__":
    main()
