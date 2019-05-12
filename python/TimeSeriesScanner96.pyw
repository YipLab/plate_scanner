# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 13:31:18 2017
YIP LAB - 2019

Acqure time series data using the linescan plate scanner
@author: Aaron Au
"""
from Tkinter import *
import tkFileDialog
import tkMessageBox
import twain
import serial
import time
import os
import numpy as np
import subprocess
import sys
from threading import Timer
from PIL import Image, ImageTk
import tifffile as tf

#VARIABLES
xyCom = "COM3"; #xy_stage COM port
well_size = 8.95; #mm
start_x = 49.0; #mm
start_y = 8.75; #mm
adj_y = -0.1; #mm
adj_x = -0.1; #mm
com_sleep = 0.5; #seconds
cap_sleep = 1; #seconds
point1_x =5*well_size; #mm
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
root.geometry("600x600")

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

labWells = Label(app, text="Wells:");
txtWells = Entry(app, width = 20);

svarInt = StringVar();
labInt = Label(app, text="Time interval(ms):");
txtInt = Entry(app, textvariable=svarInt, width = 6);
svarInt.set('3000');

svarRep = StringVar();
labRep = Label(app, text="Number of times:");
txtRep = Entry(app, textvariable=svarRep, width = 3);
svarRep.set('1');

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
        im = Image.open(file_name).crop((1000,1000,3000,3000));
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

def name_wells():
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

def name_well(col, row, orientation):
    row = row + 1
    odd = col%2 == 1
    if  not orientation:
        col = 7-col
        if not odd:
            row = 13-row
    elif odd:
        row = 13-row
    return cols[col]+str(row)

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

def checkWells():
    wells = txtWells.get()
    #break apart commas
    new_wells = []
    wells = wells.split(',')
    for well in wells:
        if (len(well) == 2 or len(well) == 3):
            #check if notation is correct
            if set(well[0]).isdisjoint(set('ABCDEFGH')):
                return [False, 'Wells need to start with the row letter']
            elif not well[1:].isdigit():
                return [False, 'Wells need to end with a integer']
            elif (int(well[1:]) == 0 or int(well[1:]) > 12): 
                return [False, 'Wells number needs to be within 1-12']
            new_wells.append(well[0]+well[1].zfill(2))
        elif (len(well) >= 5 and len(well) <= 7):
            #check if notation is correct  
            wells_split = well.split('-')
            if len(wells_split) > 2:
                return[False, "To many dashes in a range"]
            elif wells_split[0][0] != wells_split[1][0]:
                return [False, "Well range needs to be on the same row"]
            for w in wells_split:
                if set(w[0]).isdisjoint(set('ABCDEFGH')):
                    return [False, 'Wells need to start with the row letter']
                elif not w[1:].isdigit():
                    return [False, 'Wells need to end with a integer']
                elif (int(w[1:]) == 0 or int(w[1:]) > 12): 
                    return [False, 'Wells number needs to be within 1-12'] 
            #Split into individual wells
            for j in np.linspace(int(wells_split[0][1:]), int(wells_split[1][1:]), abs(int(wells_split[0][1:]) - int(wells_split[1][1:]))+1):
                new_wells.append(wells_split[0][0]+str(int(j)).zfill(2))
    #Sort wells
    new_wells.sort()
    return [True, new_wells]

def checkInt():
    check = False
    value = None
    interval = txtInt.get()
    if not interval.isdigit():
        value = "Time interval is not an integer"
    elif int(interval) < 2000:
        value = "Time interval is too short (needs to be higher than 2000ms)"
    else:
        check = True
        value = int(interval)
    return [check, value]

def checkRep():
    check = False
    value = None
    rep = txtRep.get()
    if not rep.isdigit():
        value = "Number of Reps is not an integer or is negative"
    elif rep == '0':
        value = "Number of Reps cannot be 0"
    else:
        check = True
        value = int(rep)
    return [check, value]

def scan_rep():
    global running
    global reading
    global zeroed
    global savedir
    if running:
        print 'Already Running'
    elif not checkWells()[0]:
        print checkWells()[1]
    elif not checkInt()[0]:
        print checkInt()[1]
    elif not checkRep()[0]:
        print checkRep()[1]
    else:
        #PASSED CHECKS
        wells = checkWells()[1]
        interval = checkInt()[1] #in ms
        reps = checkRep()[1]

        running = True
        reading = True
        zeroed = False
        orient = orvar.get()

        curr_x = 0
        curr_y = 0

        changeStatus('Scanning Plate')
        initCamera(camerafiles[0]);
        print('scan plate')
        sendSerial(xy_stage, "0lo1;\r\n");
        time.sleep(com_sleep);
        print(recSerial(xy_stage));
        time.sleep(com_sleep);

        for well in wells: #for each well
            #calculate movements
            next_x = cols.index(well[0])
            next_y = int(well[1:])-1
            if orient: #column 1 @ top, A @ right
                next_y = next_y
            else: #column 12 @ bottom, A @ left
                next_x = 7-next_x
                next_y = 11-next_y
            
            #move to well
            sendSerial(xy_stage, "0pr" + str((next_x-curr_x)*well_size+(next_y-curr_y)*adj_x) + ";1pr" + str((next_y-curr_y)*well_size+(next_x-curr_x)*adj_y) + ";\r\n")
            time.sleep(com_sleep);
            print(recSerial(xy_stage));

            curr_x = next_x
            curr_y = next_y

            for rep in np.linspace(0,reps-1,reps): #for each rep
                start = time.time()
                #Acquire single well
                capWell(well, rep) #CHANGE INPUTS
                root.update()

                #Wait until motor movement is finished:
                if (running == False):
                        break
                time.sleep(com_sleep);
                print(recSerial(xy_stage));
                time.sleep(com_sleep);

                if reps-1 != rep: #not last one
                    sendSerial(xy_stage, "0pr" + str(-1 * adj_x) + ";1pr" + str(-1 * well_size) + ";\r\n"); #Return to first part
                    time.sleep(com_sleep);
                    print(recSerial(xy_stage));
                    wait = interval/1000 - (time.time()-start)
                    if wait > 0:
                        time.sleep(wait) #wait for time interval
                else:
                    curr_y += 1

        stop()

def capWell(well, rep):
    ss.request_acquire(0, 0);
    time.sleep(cap_sleep);
    sendSerial(xy_stage, "1pr" + str(well_size) + ";\r\n");
    #file_name = savedir + '\\'+str(col)+ '_' + str(i) + '.tiff'
    file_name = savedir + '\\' + well+ '_' + str(rep) + '.tiff'
    ss.file_xfer_params = (file_name, 0);
    os.remove(file_name);
    ss.xfer_image_by_file();
    ss.hide_ui();
    im = Image.open(file_name);
    im.thumbnail(resize, Image.ANTIALIAS)
    changeImage(im)

#Setup Stage
print(recSerial(xy_stage));
time.sleep(com_sleep)
stop();

#Button Setup
butStart_0 = Button(app, text="Focus 1", command=focus_1)
butStart_1 = Button(app, text="Focus 2", command=focus_2)
butStart_2 = Button(app, text="Focus 3", command=focus_3)
butSavedir = Button(app, text="Directory", command=findsavedir)
butStart = Button(app, text="Start Scan", command=scan_rep)
butStop = Button(app, text="Zero", command=stop)

#Grid 
butStart_0.grid(row=0,column=0)
butStart_1.grid(row=0,column=1)
butStart_2.grid(row=0,column=2)
or_chkbtn.grid(row=1, column=0)
labstatus.grid(row=1, column=1, columnspan=3)
labWells.grid(row=2, column=0)
txtWells.grid(row=2, column=1, columnspan=3)
labInt.grid(row=3, column=0)
txtInt.grid(row=3, column=1)
labRep.grid(row=3, column=2)
txtRep.grid(row=3, column=3)
butSavedir.grid(row=4, column=0)
labsave.grid(row=4, column=1, columnspan=3)
butStart.grid(row=5, column=0)
butStop.grid(row=5, column=1)
labimage.grid(row=6, column=0, columnspan=4)

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()
