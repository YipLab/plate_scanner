import pywinauto as pywa
import time

time.sleep(0.5)

hand_bf = pywa.findwindows.find_windows(title_re='Open which')[0]
app = pywa.Application().connect(handle = hand_bf)

w = app.window_(title_re='Open which')
w.Button.ClickInput()
