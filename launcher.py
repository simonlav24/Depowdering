import PySimpleGUI as sg
import os, sys, subprocess

about_doc = """Depowdering project system launcher\nby Simon Labunsky"""

def handle_events(event, values):
    if event == 'about':
        print(about_doc)

sg.theme('Reddit')

layout =[
    [sg.Text("Depowdering Launcher")],
	[sg.Button('Play', key="play"), sg.Button('About', key="about")]
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

