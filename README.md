# Py Screen Recorder
 I just created this for my needs. But I think I may share this with those who'll need it. I use this on python 3.7.3, Windows 10. It supports an external monitor (up to 2 monitors including the built-in monitor).

## prerequisite
Need the following libraries to be installed:
* numpy
* pyautogui
* desktopmagic
* pynput
* win32api
* PIL
	
## Settings
You can just configure some constants in the main.py
Those constants are:
* `useCodec`
* `BUFFER`
* `SHOW_CURSOR`
* `FPS`

When you use multiple monitors, and the cursor seems messy, then you can modify the if-else block right
after the comment `# make a screenshot`

You can see the comments nearby the constants to read more about them. But I may WET those comments in 
this ReadMe file

### Codec and file format
Currently I just have 3 different video codec, but you can add other codecs you wish to use. It's easy.
Just assign `useCodec` variable with a tuple consists of two string, the first is the file name extension,
the second is the codec you want to use. You can find the codec on the internet :D

### Buffer
Buffer mode 0: No buffer at all. Writing to the video files right after the new screen frame is captured
Buffer mode 1: Store every picture/frame in a list/array. It consumes very high memory in a short time.
Buffer mode 2: Register a new thread to write the image. Very slowly increasing in memory to store the threads 
Buffer mode 3: Hybrid between buffer mode 1 and 2. Store frames in a list/array while having a thread to handle those frames.

Tips for the buffer mode.

It's very not recommended to disable the buffer mode, except you have a quantum computer
or supercomputer, or if you want to set the fps to 1 or lesser. Because it'll be very
slow and significantly drop your fps.

It's a little bit not recommended to use buffer mode 1, except you want to record a
less-than-one minute video and have quite big memory/RAM. Because this mode consumes
very much RAM/memory. However maintain the fps very very well (unless you're running out
of memory, which can be worse than other buffer modes in maintaining fps).

It's recommended to use either mode 2 or 3 because they're more stable in both memory and
time/fps.
Mode 2 always increased in memory, but it's very small. I think recording 1-day video will
not enough to have your memory/RAM full. However it's limited in time,
even if it's one-year-long.
However if your CPU and hard disk are not fast enough, the fps will be dropped. Unlike mode 3
which will try it's best to use memory approach to maintain the fps when the CPU is not
fast enough.

Mode 3, sometimes have bigger memory than mode 2, or nearly the same as mode 2 in memory.
Mode 3 also offers the speed/fps like mode 1 and 2. Mode 3 also won't always increase in
memory, as long as your CPU and the hard disk is fast enough to write to the video file. So,
mostly, this mode can offer you unlimited time. However, if your CPU and hard disk can't
race with the captured images, it will increase in memory but will do better than mode 2
to not drop the fps.

### SHOW_CURSOR
You can chose whether show your cursor or not in the recordings. However, your cursor in the recorded
video may not like the cursor you actually have. I just use the cursor.png to display the cursor

### FPS
You can set the fps, for one monitor and two monitor by assign the `FPS` constants with a tuple
consists of two floats. The first float is the fps when you use one monitor. The second float is
the fps when you use two monitors. It's recommended to have the second float lower/smaller than the first
