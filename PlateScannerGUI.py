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
from PIL import Image, ImageTk

#VARIABLES
xyCom = "COM3"; #xy_stage COM port
well_size = 8.95; #mm
start_x = 50; #mm
start_y = 10.75; #mm
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

#INITIALIZE GUI
root = Tk()
root.title("96 Well Plate Scanner")
root.geometry("500x500")

app = Frame(root)
app.grid();

labtext = StringVar()
labstatus = Label(app, textvariable=labtext, width=20, height=1)

cwd = os.getcwd();
vsave = StringVar()
labsave = Label(app, textvariable=vsave, width=50, height=1)
vsave.set(cwd);

labimage = Label(app, image = None);

#INITIALIZE XY STAGE
xy_stage = serial.Serial(xyCom);

#INITIALIZE CAMERA
sm = twain.SourceManager(0);
cwd = os.getcwd();
ss = sm.open_source();

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
scantime = 0 #Global counter
zeroed = False # Global indicator
savedir = cwd #Save Directory

def scanning():
    global scantime
    if running:  # Only do this if the Stop button has not been clicked
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
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        scantime = 0;
        zeroed = False;

def findsavedir():
    global savedir
    savedir = tkFileDialog.askdirectory(title="Choose Save Directory", initialdir=cwd)
    vsave.set(savedir)


def stop():
    """Stop scanning by setting the global flag to False."""
    global running
    global zeroed
    if zeroed == False:
        time.sleep(1)
        xy_stage.reset_input_buffer();
        changeStatus('Zeroing')

        sendSerial(xy_stage, "0lo0;0or;\r\n");
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        sendSerial(xy_stage,"0pr"+str(start_x)+";1pr"+str(start_y)+";\r\n");
        time.sleep(com_sleep);
        print(recSerial(xy_stage));

        running = False
        zeroed = True
        changeStatus('Ready')

def scan():
    global running
    global zeroed
    global savedir
    if running:
        print 'Already Running'
    else:
        running = True
        zeroed = False
        changeStatus('Scanning Plate')
        print('scan plate')
        sendSerial(xy_stage, "0lo1;\r\n");
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);
        for col in range(8):
            #Acquire and move
            for i in range(12):
                if (running == False):
                    break
                ss.request_acquire(0, 0);
                time.sleep(cap_sleep);
                sendSerial(xy_stage, "1pr" + str((-1) ** col * well_size) + ";\r\n");
                file_name = savedir + '\\'+str(col)+ '_' + str(i) + '.tiff'
                ss.file_xfer_params = (file_name, 0);
                os.remove(file_name);
                ss.xfer_image_by_file();
                ss.hide_ui();
                im = Image.open(file_name);
                im.thumbnail(resize, Image.ANTIALIAS)
                changeImage(im)
                root.update()

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
        
        stop()

print(recSerial(xy_stage));
time.sleep(com_sleep)
stop();

butstart_0 = Button(app, text="Focus 1", command=focus_1)
butstart_1 = Button(app, text="Focus 2", command=focus_2)
butstart_2 = Button(app, text="Focus 3", command=focus_3)
butstop = Button(app, text="Stop", command=stop)
butscan = Button(app, text="Scan Plate", command=scan)
butsavedir = Button(app, text="Directory", command=findsavedir)

butstart_0.grid(row=0,column=0)
butstart_1.grid(row=0,column=1)
butstart_2.grid(row=0,column=2)
labstatus.grid(row=1,column=0,columnspan=3)
butscan.grid(row=2,column=0)
butstop.grid(row=2, column=1)
butsavedir.grid(row=3,column=0)
labsave.grid(row=3, column=1, columnspan=3)
labimage.grid(row=4, column=0, columnspan=4)

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()