# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 13:31:18 2017

@author: Aaron Au
"""
from Tkinter import *
import tkFileDialog
import tkMessageBox
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
start_x = 49.0; #mm
start_y = 6.0; #mm
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
camerafiles = ["BitFlow Camera Interface Mid", "BitFlow Camera Interface Long"]
cols = ['A','B','C','D']
#offsets = [0, 575, 220, 100, 270, 160, 200, 100]; # offset from where to cut
#cut_dis = 8100; #pixels

#INITIALIZE GUI
root = Tk()
root.title("24 Well Plate Scanner")
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

svarTimes = StringVar();
labTimes = Label(app, text="Repeats:");
txtTimes = Entry(app, textvariable=svarTimes, width = 3);
svarTimes.set('0');

labWells = Label(app, text="Wells:");
txtWells = Entry(app, width = 20);

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
        time.sleep(cap_sleep+2.0);
        sendSerial(xy_stage, "1pr" + str((-1) ** scantime * well_size*2) + ";\r\n");
        file_name = 'test.tiff'        
        ss.file_xfer_params = (file_name, 0);
        os.remove(cwd + '\\' + file_name);
        if 'im' in vars():
            im.close();
        ss.xfer_image_by_file();
        ss.hide_ui();
        if scantime%2==0:
            im = Image.open(file_name).crop((1000,1000,3000,3000));
        else:
            im = Image.open(file_name).crop((1000,5000,3000,7000))
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
    for i in range(4):
        for k in range(2):
            im = tf.imread(savedir + "\\" + str(2*i+k)+".tiff");
            for j in range(6):
                col = i;
                row = j + 1;
                if (2*i+k)%2==1:
                    im = np.flip(im,0);
                well = cols[col]+str(row)+"_"+str(k);
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

        #t = Timer(10, name_wells) NO NEED AS IT SHOULD BE STICHED FIRST
        #t.start()
        stop()

def scan_wellbywell():
    global running
    global reading
    global zeroed
    global savedir
    if running:
        print 'Already Running'
    else:
        repeat = txtTimes.get();
        if repeat.isdigit():
            running = True
            reading = True
            zeroed = False
            orient = orvar.get()
            repeat = int(repeat);
            changeStatus('Scanning Plate')
            initCamera(camerafiles[0]);
            print('scan plate')
            sendSerial(xy_stage, "0lo1;\r\n");
            time.sleep(com_sleep);
            print(recSerial(xy_stage));
            time.sleep(com_sleep);
            for col in range(4):
                #Acquire and move
                for i in range(6):
                    if (running == False):
                        break
                    for side in range(2):
                        for j in range(repeat*2+1):
                            capWell(col, i, j, side)
                            root.update()
                        if side == 0: #Move to left side of well
                            sendSerial(xy_stage, "0pr"+str(well_size+adj_x)+";1pr"+str(adj_y+0.7*(-1)**(col)+((-1)**(col+1)*well_size*2.1))+";\r\n");
                            time.sleep(com_sleep);
                            print(recSerial(xy_stage));
                        else: #Move back to right side
                            sendSerial(xy_stage, "0pr-"+str(well_size+adj_x)+";1pr"+str(adj_y+0.7*(-1)**(col+1))+";\r\n");
                            time.sleep(com_sleep);
                            print(recSerial(xy_stage));

                #Wait until motor movement is finished:
                if (running == False):
                        break
                time.sleep(1);
                xy_stage.reset_input_buffer();
                time.sleep(1);
                
                if (col < 4 and running == True): #Move to next row
                    sendSerial(xy_stage, "0pr"+str(2*(well_size+adj_x))+";1pr"+str(2.1*(adj_y))+";\r\n");
                    time.sleep(com_sleep);
                    print(recSerial(xy_stage));
                
            stop()
        else:
            tkMessageBox.showinfo("Wrong Entry","Please input an integer into number of repeats.");

def scan_singlewell():
    global running
    global reading
    global zeroed
    global savedir
    if running:
        print 'Already Running'
    else:
        repeat = txtTimes.get();
        if repeat.isdigit():
            wells = txtWells.get().split(',');
            orient = orvar.get()
            repeat = int(repeat);
            for well in wells:
                running = True
                reading = True
                zeroed = False
                changeStatus('Scanning Plate')
                #Move to well
                if well[0] in cols and well[1:].isdigit():
                    col = cols.index(well[0]);
                    row = int(well[1:])-1;
                    if (row <= 6 and row >= 0):
                        sendSerial(xy_stage, "0pr"+str((well_size*2+adj_x)*col)+";1pr"+str(well_size*2.1*(row+int(col%2==1))+adj_y*col*2.1)+";\r\n");
                        print(recSerial(xy_stage));
                        initCamera(camerafiles[0]);
                        print('scan plate')
                        sendSerial(xy_stage, "0lo1;\r\n");
                        time.sleep(com_sleep);
                        print(recSerial(xy_stage));
                        time.sleep(com_sleep);
                        if col%2==1:
                            row = 6-row;
                        for side in range(2):
                            for j in range(repeat*2+1):
                                capWell(col, row, j, side)
                                root.update()
                            if side == 0: #Move to left side of well
                                sendSerial(xy_stage, "0pr"+str(well_size+adj_x)+";1pr"+str(adj_y+0.7*(-1)**(col)+((-1)**(col+1)*well_size*2.1))+";\r\n");
                                time.sleep(com_sleep);
                                print(recSerial(xy_stage));
                stop()
        else:
            tkMessageBox.showinfo("Wrong Entry","Please input an integer into number of repeats.");

def capWell(col, i, j, k):
    i=i+1;
    if col%2==1:
        i = 7-i;
    ss.request_acquire(0, 0);
    time.sleep(cap_sleep+2.0);
    sendSerial(xy_stage, "1pr" + str((-1) ** (col+j) * well_size*2.1) + ";\r\n");
    #file_name = savedir + '\\'+str(col)+ '_' + str(i) + '.tiff'
    file_name = savedir + '\\' + cols[col]+ str(i) + '_' + str(k) + '_' + str(j) + '.tiff'
    ss.file_xfer_params = (file_name, 0);
    os.remove(file_name);
    ss.xfer_image_by_file();
    ss.hide_ui();
    im = Image.open(file_name);
    im.thumbnail(resize, Image.ANTIALIAS)
    changeImage(im)

    print(recSerial(xy_stage));

stop();

butstart_0 = Button(app, text="Focus 1", command=focus_1)
butstart_1 = Button(app, text="Focus 2", command=focus_2)
butstart_2 = Button(app, text="Focus 3", command=focus_3)
butstop = Button(app, text="Zero", command=stop)
butscan = Button(app, text="Scan Plate", command=scan)
butwbw = Button(app, text="Scan Well by Well", command=scan_wellbywell)
butindw = Button(app, text="Scan Indicated Wells", command=scan_singlewell)
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
butwbw.grid(row=4,column=2)
labTimes.grid(row=4,column=0)
txtTimes.grid(row=4,column=1)
labWells.grid(row=5,column=0)
txtWells.grid(row=5,column=1,columnspan=3)
butindw.grid(row=5,column=4)
labimage.grid(row=6, column=0, columnspan=6)

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()
