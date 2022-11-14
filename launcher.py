import PySimpleGUI as sg
import os, sys, subprocess
from model3D import Model

about_doc = """Depowdering project system launcher\nby Simon Labunsky"""

def evaluate_model(filename):
    if not filename.endswith('.obj'):
        sg.Popup('Sorry, only .obj files are supported')

def handle_events(event, values):
    # print(event, values)
    if event == 'about':
        sg.Popup(about_doc)

    if event == 'browse':
        filename = sg.PopupGetFile('Select model to open', no_window=True)
        if filename:
            window['--model-path'].update(filename)
        evaluate_model(filename)

    if event == 'browse_input':
        filename = sg.PopupGetFile('Select input file', no_window=True)
        if filename:
            window['--rotation-input'].update(filename)

    if event =='play':
        string = 'py ./main3D.py '
        for key in values:
            if key == '--rotation-input':
                if values[key] == '':
                    continue
            if '--' in key:
                string += key + ' ' + str(values[key]) + ' '
        print('executing: ' + string)
        subprocess.Popen(string, shell=True)

sg.theme('Reddit')

layout =[
    [sg.Text("------ Depowdering Launcher ------")],
    [sg.Text('Model Path'), sg.Input('', key='--model-path'), sg.Button('Browse', key='browse')],
    [sg.Text('Rotation Input Path'), sg.Input('', key='--rotation-input'), sg.Button('Browse', key='browse_input')],
    [sg.Text('------ Powder Grid Settings ------')],
    [sg.Text('Grid Size'), sg.Spin([i for i in range(1, 100)], size=(6, 1), initial_value=30, key='--grid-size')
        , sg.Text('Grid Points'), sg.Spin([i for i in range(1, 100, 2)], size=(6, 1), initial_value=5, key='--grid-points')],
    [sg.Text('------ Animation Settings ------')],
    [sg.Text('Animation Speed'), sg.Slider(range=(1, 100), orientation='h', size=(20, 15), default_value=50, key='--animation-speed')],
	[sg.Button('Play', key="play"), sg.Button('About', key="about")],
    ]

# Create the Window
window = sg.Window('Depowdering Launcher', layout)

while True:
    event, values = window.read()
    handle_events(event, values)

    if event == sg.WIN_CLOSED:
        break
        
    window.Refresh()
window.close()

