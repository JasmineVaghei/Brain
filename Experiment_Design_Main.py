import random
from psychopy.visual import Window, ShapeStim, Line
from psychopy import core, visual
from pylsl import StreamInfo, StreamOutlet

from psychopy.hardware import keyboard

BLACK, WHITE = (-1, -1, -1), (1, 1, 1)
defaultKeyboard = keyboard.Keyboard()

n_trials = 60
REFRESH_RATE = 60  # Set the refresh rate of the screen
WIN_SIZE = 1920, 1080  # Window size


def draw_cross():
    cross_line1 = Line(win=win, units="pix", lineColor=BLACK, lineWidth=5)
    cross_line1.start = [-200, 0]
    cross_line1.end = [+200, 0]
    cross_line2 = Line(win=win, units="pix", lineColor=BLACK, lineWidth=5)
    cross_line2.start = [0, -200]
    cross_line2.end = [0, +200]
    cross_line1.draw()
    cross_line2.draw()


trial_labels = [2, 3, 4, 5]
n_trials_per_class = int(n_trials/len(trial_labels))

MI_trials = trial_labels * n_trials_per_class
random.shuffle(MI_trials)

win = Window(size=WIN_SIZE, fullscr=True, color=WHITE, units="pix", screen=-1)

info = StreamInfo(name="LSL_Markers", type="Markers", channel_count=1,
                  channel_format="int32", source_id="LSL_Markers_001")
outlet = StreamOutlet(info)

# Just an example of some basic shapes:
verts_right = [(0, 30), (200, 30), (200, 50),
               (300, 0), (200, -50), (200, -30), (0, -30)]
right = ShapeStim(win, fillColor='black', vertices=verts_right,
                  lineColor='black', opacity=1)

verts_left = [(0, 30), (-200, 30), (-200, 50),
              (-300, 0), (-200, -50), (-200, -30), (0, -30)]
left = ShapeStim(win, fillColor='black', vertices=verts_left,
                 lineColor='white', opacity=1)

verts_down = [(30, 0), (30, -200), (50, -200),
              (0, -300), (-50, -200), (-30, -200), (-30, 0)]
down = ShapeStim(win, fillColor='black', vertices=verts_down,
                 lineColor='black', opacity=1)
verts_up = [(30, 0), (30, 200), (50, 200),
              (0, 300), (-50, 200), (-30, 200), (-30, 0)]
up = ShapeStim(win, fillColor='black', vertices=verts_up,
                 lineColor='black', opacity=1)

textstimlike=visual.TextBox( window=win,text="Please go back to your initial position.", font_size=24, font_color=[-1,-1,-1], color_space='rgb', size=(1.8,.1), pos=(0.5,0.5), units='norm')

core.wait(10)

# Pushing different markers to the LSL stream:
# 1 for the appearing cross or the begin of the trial
# 2 for the arrow pointing to the left
# 3 for the arrow pointing to the right
# 4 for the arrow pointing downward
# 5 for the arrow pointing up
# 8 for the disappearing cross or the end of the MI trial

for MI_trial in MI_trials:
    if defaultKeyboard.getKeys(keyList=['escape']):  # Abort with Esc
        core.quit()
    for iframe in range(round(2*REFRESH_RATE)):  # 0-2s: only cross
        draw_cross()
        if iframe == 0:
            win.callOnFlip(outlet.push_sample, x=[0])
        win.flip()
    for iframe in range(round(5*REFRESH_RATE)):  # 2-7s: cue
        draw_cross()
        if MI_trial == 2:
            left.draw()
        elif MI_trial == 3:
            right.draw()
        elif MI_trial == 4:
            down.draw()
        elif MI_trial == 5:
            up.draw()
        if iframe == 0:
            win.callOnFlip(outlet.push_sample, x=[MI_trial])
        win.flip()
    for iframe in range(round(5*REFRESH_RATE)):  # 7-12s: Blank
        #win.flip()
        textstimlike.draw()
    win.callOnFlip(outlet.push_sample, x=[8])  # end of trial
    win.flip()
    core.wait(random.randint(2000, 5000)/1000)  # random inter-trial interval
win.close()
