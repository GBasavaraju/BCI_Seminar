from pathlib import Path
import tkinter as tk
import tkinter.font as font
import datetime
import winsound
import random

# WINDOW CONFIG
app = tk.Tk()
app.title("Mental Workload | Autonmous Driving")
app.geometry('500x525')

####
# CONSTANTS
# StrVars
AUTO_TRUE = tk.StringVar()
AUTO_TRUE.set('TRUE')
AUTO_FALSE = tk.StringVar()
AUTO_FALSE.set('FALSE')
HIGH_LEVEL = tk.StringVar()
HIGH_LEVEL.set('HIGH')
LOW_LEVEL = tk.StringVar()
LOW_LEVEL.set('LOW')

# Colors

# Update Intervall
INTERVALL = 1000

# Bold font
BOLD_FONT = font.Font(weight='bold')
SMALL_FONT = ('Helvetica', '8', 'normal')
IMAGE_FONT = ('Arial', '20', 'bold')

####
# State globals
state = 0
state_change = 0
state_log_list_short = [0]
state_log_list_full = [0]


####
# Frames
class StatsFrame:
    """
    Labels in frame showing relevant values
    - Suggest Value: True/False autopilot suggestion based on MWL
    - current state: current MWL level
    - change state: MWL rising or falling
    - timer: seconds from start    
    """
    def __init__(self, parent):
        self.seconds = 0
        self.stats_frame = tk.LabelFrame(parent, text='Info', padx=10, pady=10, width=30)
        # text labels
        self.suggest_lbl = tk.Label(self.stats_frame, text="Suggest Autopilot")
        self.current_state_lbl = tk.Label(self.stats_frame, text='Current Level')
        self.change_state_lbl = tk.Label(self.stats_frame, text='Change State')
        self.timer_lbl = tk.Label(self.stats_frame, text='Time Since Start')
        #value labels
        self.suggest_value = tk.Label(self.stats_frame, textvariable=AUTO_FALSE, width=10, height=1)
        self.current_state_value = tk.Label(self.stats_frame, textvariable=LOW_LEVEL)
        self.change_state_value = tk.Label(self.stats_frame, text=0)
        self.timer_value = tk.Label(self.stats_frame, text='0 s')
        # customize
        self.suggest_value['font'] = BOLD_FONT

        # pack frame
        self.stats_frame.pack()
        self.stats_frame.pack_propagate(0)

        # grid text labels
        self.suggest_lbl.grid(column=0, row=0, padx=5, pady=5, columnspan=1)
        self.current_state_lbl.grid(column=0, row=1, padx=5, pady=5, sticky='w')
        self.change_state_lbl.grid(column=0, row=2, padx=5, pady=5, sticky='w')
        self.timer_lbl.grid(column=0, row=3, padx=5, pady=5, sticky='w')
        # grid value labels
        self.suggest_value.grid(column=1, row=0, padx=5, pady=5)
        self.current_state_value.grid(column=1, row=1, padx=5, pady=5)
        self.change_state_value.grid(column=1, row=2, padx=5, pady=5)
        self.timer_value.grid(column=1, row=3, padx=5, pady=5)


    def update_labels(self):
        # updates StatsFrame
        self.update_suggest()
        self.update_state()
        self.update_change()
        self.update_timer()
        self.stats_frame.after(INTERVALL, self.update_labels)   


    def update_suggest(self):
        # sets text of suggestion value label to True or False based on state
        #global state
        if not state:
            self.suggest_value.configure(textvariable=AUTO_FALSE)
        else:
            self.suggest_value.configure(textvariable=AUTO_TRUE)
            
        
    def update_state(self):
        # sets text of state label to state
        if not state:
            self.current_state_value.configure(textvariable=LOW_LEVEL)
        else:
            self.current_state_value.configure(textvariable=HIGH_LEVEL)
        #self.current_state_value.configure(text=str(state))

    def update_change(self):
        # sets text of change state value to state_change
        self.change_state_value.configure(text=str(state_change))

    def update_timer(self):
        # updates timer
        self.seconds += 1
        self.timer_value.configure(text=" {} s ".format(self.seconds))
        #self.timer_value.after(INTERVALL, self.update_timer)


class LogFrame:
    """
    Logs 
    - time: %H %M %s
    - curent state: (0, low) (1, high)
    - state change: (0, no change) (1, rising) (2, falling)
    - suggest: True|False
    """
    def __init__(self, parent):
        # TODO: rework seconds in single object (LogFrame/StatsFrame)
        self.seconds = 0
        self.timestring = '0:00:00'
        self.log_str = '0:00:00 (0, low) (0, no change) False\n'

        self.log_frame = tk.LabelFrame(parent, width=35, height=6, text='Log')
        self.log_text = tk.Text(self.log_frame, width=34, height=5)
        self.log_scrollbar = tk.Scrollbar(self.log_frame)

        self.log_text.configure(font=SMALL_FONT)
        self.log_frame.pack()
        self.log_text.pack(side=tk.LEFT)
        self.log_scrollbar.pack(side=tk.RIGHT)

    
    def build_state_str(self):
        # (0, low) (1, high)
        if not state:
            return str((0, 'low'))
        else:
            return str((1, 'high'))


    def build_change_str(self):
        # (0, no change) (1, rising) (2, falling)
        if not state_change:
            return str((0, 'no change'))
        if state_change:
            return str((1, 'rising'))
        else:
            return str((2, 'falling'))


    def build_suggest_str(self):
        # True | False
        if not state:
            return str(False)
        return str(True)


    def build_log_string(self):
        self.update_time()
        self.format_time()
        time = self.timestring
        state_str = self.build_state_str()
        change_str = self.build_change_str()
        suggest_str = self.build_suggest_str()
        self.log_str = time+' '+state_str+' '+change_str+' '+suggest_str+'\n'


    def print_log(self):
        self.build_log_string()
        self.log_text.insert(tk.END, self.log_str)
        self.log_text.see('end')
        self.log_text.after(1000, self.print_log)
        

    def update_time(self):
        self.seconds += 1


    def print_time(self):
        self.log_text.insert(tk.END, '{}\n'.format(self.timestring))
        self.update_time()
        self.format_time()
        self.log_text.after(1000, self.print_time)


    def format_time(self):
        self.timestring = str(datetime.timedelta(seconds=self.seconds))
        #return str(datetime.timedelta(seconds=self.seconds))


class ImageFrame:
    """
    Displays Images based on state and state_change.
    Consists of labels holding the respective Images and activates and disables them.
    """
    def __init__(self, parent):
        self.parent = parent
        self.rising = False
        self.falling = False
        self.no_change = True

        self.happy_driving = tk.StringVar()
        self.happy_driving.set('Happy Driving')
        self.activate_autopilot = tk.StringVar()
        self.activate_autopilot.set('Activate Autopilot!')
    
        # place coordinates
        self.rise_place = {'relx': 0.65, 'rely': 0.7}
        self.fall_place = {'relx': 0.25, 'rely': 0.7}
        self.no_change_place = {'relx': 0.5, 'rely': 0.85, 'anchor': tk.CENTER}
        self.load_place = {'relx': 0.5, 'rely': 0.25, 'anchor':tk.CENTER}
        self.load_text_place = {'relx':0.5, 'rely': 0.6,'anchor':  tk.CENTER}
        # frame
        self.img_frame = tk.Frame(parent, width=500, height=350, pady=5, borderwidth=1, relief='groove')
        self.img_frame.pack()
        # load images
        self.no_change_on_img = tk.PhotoImage(file=get_asset_path('no_change_on.gif'))
        self.no_change_off_img = tk.PhotoImage(file=get_asset_path('no_change_off.gif'))
        self.rise_active_img = tk.PhotoImage(file=get_asset_path('rising_active.gif'))
        self.rise_disabled_img = tk.PhotoImage(file=get_asset_path('rising_disabled.gif'))
        self.fall_active_img = tk.PhotoImage(file=get_asset_path('falling_active.gif'))
        self.fall_disabled_img = tk.PhotoImage(file=get_asset_path('falling_disabled.gif'))

        self.high_load_img = tk.PhotoImage(file=get_asset_path('warning.gif'))
        self.low_load_img = tk.PhotoImage(file=get_asset_path('happy_driving.gif'))
        # store images in Labels
        self.no_change_on = tk.Label(self.img_frame, image=self.no_change_on_img)
        self.no_change_off = tk.Label(self.img_frame, image=self.no_change_off_img)
        self.rise_active = tk.Label(self.img_frame, image=self.rise_active_img)
        self.rise_disabled = tk.Label(self.img_frame, image=self.rise_disabled_img)
        self.fall_active = tk.Label(self.img_frame, image=self.fall_active_img)
        self.fall_disabled = tk.Label(self.img_frame, image=self.fall_disabled_img)
        self.high_load = tk.Label(self.img_frame, image=self.high_load_img)
        self.low_load = tk.Label(self.img_frame, image=self.low_load_img)
        self.load_text = tk.Label(self.img_frame, textvariable=self.happy_driving)
        self.load_text.config(font=IMAGE_FONT)
        # place labels
        self.no_change_on.place(**self.no_change_place)
        self.rise_disabled.place(**self.rise_place)
        self.fall_disabled.place(**self.fall_place)
        self.low_load.place(**self.load_place)
        self.load_text.place(**self.load_text_place)

    
    def update_frame(self):
        self.update_load_img_text()
        self.img_frame.after(INTERVALL, self.update_frame)


    def check_rise(self):
        if state_change:
            self.activate_rise_label()
            print('Rise '+str(self.rising))
    

    def update_rise_fall(self):
        #print(state_change)
        #print(state_change == 1)
        #print(type(state_change))

        if state_change:
            # TODO not going into condition???? Probably loop issues
            # == 1 -> rising
            self.rising = True
            self.falling = False
            self.no_change = False
        

    def update_load_img_text(self):
        # updates center image based on state
        if not state:
            self.activate_happy_text()
            self.activate_happy_img()
        else:
            self.activate_autopilot_text()
            self.disable_happy_img()


    def update_change_labels(self):
        if self.rising:
            self.activate_rise_label()
            self.disable_fall_label()
            self.disable_no_change_label()
        if self.falling:
            self.activate_fall_label()
            self.disable_rise_label()
            self.disable_no_change_label()
        else:
            self.activate_no_change_label()
            self.disable_rise_label()
            self.disable_fall_label()


    def activate_happy_img(self):
        self.low_load.place(**self.load_place)
        self.high_load.place_forget()

    
    def disable_happy_img(self):
        self.high_load.place(**self.load_place)
        self.low_load.place_forget()


    def activate_happy_text(self):
        self.load_text.config(textvariable=self.happy_driving)

    
    def activate_autopilot_text(self):
        self.load_text.config(textvariable=self.activate_autopilot)


    def activate_rise_label(self):
        self.rise_active.place(**self.rise_place)
        self.rise_disabled.place_forget()


    def disable_rise_label(self):
        self.rise_disabled.place(**self.rise_place)
        self.rise_active.place_forget()    


    def activate_fall_label(self):
        self.fall_active.place(**self.fall_place)
        self.fall_disabled.place_forget()


    def disable_fall_label(self):
        self.fall_disabled.place(**self.fall_place)
        self.fall_active.place_forget()

    
    def activate_no_change_label(self):
        self.no_change_on.place(**self.no_change_place)
        self.no_change_off.place_forget()


    def disable_no_change_label(self):
        self.no_change_off.place(**self.no_change_place)
        self.no_change_on.place_forget() 


###
# UTIL
def play_sound():
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 500  # Set Duration To update_frequency ms == 1 second
    winsound.Beep(frequency, duration)
    winsound.Beep(frequency, duration)


def play_sound_high_load():
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 200  # Set Duration To update_frequency ms == 1 second
    winsound.Beep(frequency, duration)


def play_sound_falling():
    # sound plaxed when load is falling
    frequency = 1500
    duration = 1700
    winsound.Beep(frequency, duration)


def is_change():
    """
    0: no change
    1: rising   low->high
    2: falling  high->low

    also updates img_frame change labels
    TODO put img_frame somewhere else
    """
    global state_change

    if state_log_list_short[0] == state_log_list_short[1]:
        # no change
        state_change = 0
        img_frame.activate_no_change_label()
        img_frame.disable_fall_label()
        img_frame.disable_rise_label()
        if state==1:
            play_sound_high_load()
        return 0
    if state_log_list_short[0] < state_log_list_short[1]:
        # rising
        state_change = 1
        img_frame.activate_rise_label()
        img_frame.disable_no_change_label()
        img_frame.disable_fall_label()
        return 1
    if state_log_list_short[0] > state_log_list_short[1]:
        # falling
        state_change = 2
        img_frame.activate_fall_label()
        img_frame.disable_rise_label()
        img_frame.disable_no_change_label()
        play_sound_falling()
        return 2


def get_state(input):
    """
    Gets state from file/input, sets the state, updates change based on previous and current state

    input
    - 0: from file
    - 1: from rng
    """
    global state
    global state_log_list_short
    global state_log_list_full
    
    if input:
        state = random_number()
    else:
        state = read_file(predict_txt_path)
    #state = readFile(filepath)

    # log list 
    state_log_list_short.append(state)
    state_log_list_full.append(state)

    if len(state_log_list_short) > 2:
        state_log_list_short.pop(0)
    
    is_change()
    app.after(INTERVALL, get_state, input)


def random_number():
    # random dummy input sequence
    values = [0,1]
    return random.choice(values)


def read_file(filepath):
    # gets last value of txt input file
    with open(filepath,'r') as f:
        new_lines = f.readlines()
        if not new_lines:
            return 0
        else:
            new_line = new_lines[-1].strip()
            return int(new_line)


def get_asset_path(filename):
    # build total of file in assets subfolder
    location = Path(__file__).absolute().parent
    filepath = location / './assets/{}'.format(filename)
    return filepath


def get_file_path(filename):
    location = Path(__file__).absolute().parent
    filepath = location / filename
    return filepath


# read predict.txt
predict_txt_path = get_file_path('predict.txt')
read_file(predict_txt_path)

# inst frames
#lights = LightsCanvas(app)
img_frame = ImageFrame(app)

# log stats side by side
log_stat_frame = tk.Frame(app)
log_stat_frame.pack()
# infobox and logbox children of log_stat_frame
stats = StatsFrame(log_stat_frame)
log_frame = LogFrame(log_stat_frame)
# pack stats to left
stats.stats_frame.pack(side=tk.LEFT)

# update frames
# 0 to get file input
# 1 to get dummy input

# update global state 
app.after(INTERVALL, get_state, 0)
# update img_frame
app.after(INTERVALL, img_frame.update_frame)
# print log
app.after(INTERVALL, log_frame.print_log)
# update info labels
app.after(INTERVALL, stats.update_labels)


# mainloop
app.mainloop()