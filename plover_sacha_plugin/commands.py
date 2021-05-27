import os
import subprocess
import re
import requests

SPECTRA_URL='http://127.0.0.1:8081'

def emacsclient(engine, argument):
    global state
    subprocess.Popen(["emacsclient", "-e", argument])

def get_last_clippy(engine):
    line = subprocess.check_output(['tail', '-1', os.path.join(os.path.dirname(engine._config.path), 'clippy.txt')]).decode('utf-8')
    m = re.match('[^]]+\] (.*?)[ \t]+\|\| (.*?) -> ([^\n]+)', line)
    translation = m.group(1)
    alternatives = m.group(3)
    strokes = re.split(', ', alternatives)
    return {'translation': translation, 'alternatives': alternatives, 'strokes': strokes}

def spectra_last_clippy_command(engine, args):
    last_clippy = get_last_clippy(engine)
    data = last_clippy['translation']
    subprocess.run(["xclip", '-selection', 'clipboard'], universal_newlines=True, input=data)
    print(data)
    subprocess.run(['xdotool', 'search', '--onlyvisible', '--name', 'The Spectra Project', 'windowactivate', '--sync', 'mousemove', '67', '130', 'click', '1', 'key', 'ctrl+a', 'ctrl+v', 'sleep', '0.5', 'mousemove', '73', '164', 'click', '1'])
    
def notify_last_clippy_command(engine, args):
    last_clippy = get_last_clippy(engine)
    info = "%s -> %s" % (last_clippy['translation'], last_clippy['alternatives'])
    subprocess.call(['notify-send', info, "--expire-time", "3000"])
    
def notify(engine, args):
    subprocess.call(['notify-send', args, "--expire-time", "3000"])

   #   curl 'http://localhost:8081/request' \
   # -H 'Content-Type: application/json' \
   # --data-raw '{"action":"query_match","args":["test",["T*ES","TEF","TEFLT","TEFT"]],"options":{"search_mode_strokes":false,"search_mode_regex":false,"board_aspect_ratio":4.676,"board_show_compound":1,"board_show_letters":1}}' \

def get_spectra_rules(translation, outline):
    global SPECTRA_URL
    json_data = {'action': 'query_match', 'args': [translation, outline], 'options': {'search_mode_strokes': False, 'search_mode_regex': False, 'board_aspect_ratio': 4.676, 'board_show_compound': 1, 'board_show_letters': 1}}
    r = requests.post(SPECTRA_URL + '/request', json=json_data)
    return [x['caption'] for key, x in list(r.json()['display']['pages_by_ref'].items())[1:]]
    
def get_spectra_svg(translation, outlines):
    global SPECTRA_URL
    json_data = {'action': 'query_match', 'args': [translation, outlines], 'options': {'search_mode_strokes': False, 'search_mode_regex': False, 'board_aspect_ratio': 4.676, 'board_show_compound': 1, 'board_show_letters': 1}}
    print(json_data)
    r = requests.post(SPECTRA_URL + '/request', json=json_data)
    return r.json()['display']['default_page']['board']
    
def anki_last_clippy_command(engine, args):
    last_clippy = get_last_clippy(engine)
    DECK_NAME = 'My words'
    NOTE_TYPE = 'Type in steno and show diagram'
    r = requests.post('http://127.0.0.1:8765', json={
        'action': 'addNote',
        'version': 6,
        'params': {
            'note': {
                'deckName': DECK_NAME,
                'modelName': NOTE_TYPE,
                'fields': {
                    'Front': last_clippy['translation'],
                    'Back': last_clippy['strokes'][0],
                    'Notes': last_clippy['alternatives']
                },
                'tags': ['clippy']
            }
        }
    })
    result = r.json()
    if result['error'] is None:
        notify(engine, 'added Anki note for ' + last_clippy['translation'])
    else:
        notify(engine, 'error adding Anki note: ' + result['error'])
    print(r.json())

def toggle_window(engine, args):
    args = re.split(':', args)
    if len(args) == 1:
        type = 'name'
        id = args[0]
    else:
        type = args[0]
        id = args[1]
    current_wid = subprocess.run(['xdotool', 'getwindowfocus'], stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
    type_flag = '--' + type
    matching_wids = subprocess.run(['xdotool', 'search', type_flag, id], stdout=subprocess.PIPE).stdout.decode('utf-8')
    matching_wids = re.split('\n', matching_wids)
    if current_wid in matching_wids:
        subprocess.run(['xdotool', 'key', 'Alt+Tab'])
    else:
        subprocess.run(['xdotool', 'search', '--onlyvisible', type_flag, id, 'windowactivate'])
        
    
