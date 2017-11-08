# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 13:31:18 2017

@author: Aaron Au
"""
from Tkinter import *
import tkFileDialog
import twain
import serial
import time
import os
import subprocess
import sys
from threading import Timer
from PIL import Image, ImageTk
import tifffile as tf

#VARIABLES
xyCom = "COM3"; #xy_stage COM port
well_size = 8.95; #mm
start_x = 51; #mm
start_y = 11.75; #mm
adj_y = -0.1; #mm
adj_x = -0.1; #mm
com_sleep = 1; #seconds
cap_sleep = 1; #seconds
point1_x =4.5*well_size; #mm
point1_y =0; #mm
point2_x =0; #mm
point2_y =11*well_size; #mm
point3_x =7*well_size; #mm
point3_y =11*well_size; #mm
resize = 500,500; #Image Size
camerafiles = ["BitFlow Camera Interface Short", "BitFlow Camera Interface Long"]
cols = ['A','B','C','D','E','F','G','H']
offsets = [0, 575, 220, 100, 270, 160, 200, 100]; # offset from where to cut
cut_dis = 4050; #pixels 

#INITIALIZE GUI
root = Tk()
root.title("96 Well Plate Scanner")
root.geometry("600x550")

app = Frame(root)
app.grid();

labtext = StringVar()
labstatus = Label(app, textvariable=labtext, width=20, height=1)

orvar = BooleanVar()
or_chkbtn = Checkbutton(app, text="Column 1 at top", variable=orvar)

cwd = os.getcwd();
vsave = StringVar()
labsave = Label(app, textvariable=vsave, width=50, height=1)
vsave.set(cwd);

labimage = Label(app, image = None, borderwidth=3, relief="solid");

#INITIALIZE XY STAGE
xy_stage = serial.Serial(xyCom);

#INITIALIZE CAMERA
global sm, ss
sm = twain.SourceManager(0);
subprocess.Popen([sys.executable, "winauto.py"])
ss = sm.open_source(camerafiles[0])

cwd = os.getcwd();

def initCamera(source):
    global ss
    global sm
    if (ss._state == "open"):
        ss.destroy()
    subprocess.Popen([sys.executable, "winauto.py"])
    ss = sm.open_source(source)

def sendSerial(com, command):
    print(command);
    com.write(command);
    
def recSerial(com):
    return com.readline();


def changeStatus(stat):
    labtext.set(stat);
    labstatus.update_idletasks();

def changeImage(img):
    img = ImageTk.PhotoImage(img)
    labimage.configure(image=img)
    labimage.image=img
    labimage.update_idletasks()


running = False  # Global flag
reading = False
scantime = 0 #Global counter
zeroed = False # Global indicator
savedir = cwd #Save Directory

def scanning():
    global scantime
    if (running and not reading):  # Only do this if the Stop button has not been clicked
        print "scanning"
        changeStatus('Focusing')
        ss.request_acquire(0, 0);
        time.sleep(cap_sleep);
        sendSerial(xy_stage, "1pr" + str((-1) ** scantime * well_size) + ";\r\n");
        file_name = 'test.tiff'        
        ss.file_xfer_params = (file_name, 0);
        os.remove(cwd + '\\' + file_name);
        if 'im' in vars():
            im.close();
        ss.xfer_image_by_file();
        ss.hide_ui();
        im = Image.open(file_name);
        im.thumbnail(resize, Image.ANTIALIAS)
        changeImage(im)
        scantime += 1

    # After 1 second, call scanning again (create a recursive loop)
    root.update()
    root.after(1000, scanning)

def focus_1():
    """Enable scanning by setting the global flag to True."""
    global running
    global scantime
    global zeroed
    if running:
        print 'Already Running'
    else: 
        running = True
        changeStatus('Focus 1')
        sendSerial(xy_stage,"0pr"+str(point1_x)+";1pr"+str(point1_y)+";0lo1;\r\n");
        initCamera(camerafiles[0]); 
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        scantime = 0;
        zeroed = False;
        
def focus_2():
    """Enable scanning by setting the global flag to True."""
    global running
    global scantime
    global zeroed
    if running:
        print 'Already Running'
    else: 
        running = True
        changeStatus('Focus 2')
        sendSerial(xy_stage,"0pr"+str(point2_x)+";1pr"+str(point2_y)+";0lo1;\r\n");
        initCamera(camerafiles[0]); 
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        scantime = 0;
        zeroed = False;
        
def focus_3():
    """Enable scanning by setting the global flag to True."""
    global running
    global scantime
    global zeroed
    if running:
        print 'Already Running'
    else: 
        running = True
        changeStatus('Focus 3')
        sendSerial(xy_stage, "0pr" + str(point3_x) + ";1pr" + str(point3_y) + ";0lo1;\r\n");
        initCamera(camerafiles[0]); 
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        scantime = 0;
        zeroed = False;

def findsavedir():
    global savedir
    savedir = tkFileDialog.askdirectory(title="Choose Save Directory", initialdir=cwd)
    vsave.set(savedir)

def name_well():
    global savedir
    for i in range(8):
        im = tf.imread(savedir + "\\" + str(i)+".tiff");
        for j in range(12):
            col = i;
            row = j + 1;
            if not orvar.get():
                col = 7-col;
                if  col%2 == 1:
                    row = 13-row;
            elif col%2 == 1:
                row = 13-row;
            well = cols[col]+str(row);
            tf.imsave(savedir + "\\" + well +".tiff", im[j*cut_dis+offsets[i]:(j+1)*cut_dis+offsets[i],:]);

def stop():
    """Stop scanning by setting the global flag to False."""
    global running
    global reading
    global zeroed
    global ss
    if zeroed == False:
        time.sleep(1)
        xy_stage.reset_input_buffer();
        changeStatus('Zeroing')
        sendSerial(xy_stage, "0lo0;0or;\r\n");
        ss.destroy();
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        sendSerial(xy_stage,"0pr"+str(start_x)+";1pr"+str(start_y)+";\r\n");
        time.sleep(com_sleep);
        print(recSerial(xy_stage));

        running = False
        reading = False
        zeroed = True
        changeStatus('Ready')

def scan():
    global running
    global reading
    global zeroed
    global savedir
    global ss
    if running:
        print 'Already Running'
    else:
        running = True
        reading = True
        zeroed = False
        orient = orvar.get()
        changeStatus('Scanning Plate')
        print('scan plate')
        initCamera(camerafiles[1]);
        ss.request_acquire(0,0);
        sendSerial(xy_stage, "0lo1;\r\n");
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        for col in range(8):
            """#Acquire and move
            for i in range(12):
                if (running == False):
                    break
                ss.request_acquire(0, 0);
                time.sleep(cap_sleep);
                sendSerial(xy_stage, "1pr" + str((-1) ** col * well_size) + ";\r\n");
                #file_name = savedir + '\\'+str(col)+ '_' + str(i) + '.tiff'
                file_name = savedir + '\\' + name_well(col,i,orient) + '.tiff'
                ss.file_xfer_params = (file_name, 0);
                os.remove(file_name);
                ss.xfer_image_by_file();
                ss.hide_ui();
                im = Image.open(file_name);
                im.thumbnail(resize, Image.ANTIALIAS)
                changeImage(im)
                root.update()"""
            file_name = savedir + '\\'+str(col)+ '.tiff';
            ss.file_xfer_params = (file_name, 0);
            os.remove(file_name);
            t = Timer(13.0, sendSerial, [xy_stage, "1pr" + str((-1) ** col * 12 * well_size) + ";\r\n"])
            t.start();
            time.sleep(5);
            ss.xfer_image_by_file();
            #ss.hide_ui();
            root.update();

            #Wait until motor movement is finished:
            if (running == False):
                break
            time.sleep(1);
            xy_stage.reset_input_buffer();
            time.sleep(1);
        
            if (col < 7 and running == True): #Move to next row
                sendSerial(xy_stage, "0pr"+str(well_size+adj_x)+";1pr"+str(adj_y)+";\r\n");
                time.sleep(com_sleep);
                print(recSerial(xy_stage));

        t = Timer(10, name_well)
        t.start()
        stop()

print(recSerial(xy_stage));
time.sleep(com_sleep)
stop();

butstart_0 = Button(app, text="Focus 1", command=focus_1)
butstart_1 = Button(app, text="Focus 2", command=focus_2)
butstart_2 = Button(app, text="Focus 3", command=focus_3)
butstop = Button(app, text="Zero", command=stop)
butscan = Button(app, text="Scan Plate", command=scan)
butsavedir = Button(app, text="Directory", command=findsavedir)

butstart_0.grid(row=0,column=0)
butstart_1.grid(row=0,column=1)
butstart_2.grid(row=0,column=2)
butstop.grid(row=0, column=3)
labstatus.grid(row=1,column=0,columnspan=2)
butsavedir.grid(row=2,column=0)
labsave.grid(row=2, column=1, columnspan=4)
or_chkbtn.grid(row=3, column=0, columnspan=2)
butscan.grid(row=3,column=2)
labimage.grid(row=4, column=0, columnspan=5)

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()
