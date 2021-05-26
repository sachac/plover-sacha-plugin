import os
import subprocess
import re
import requests

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

def notify_last_clippy_command(engine, args):
    last_clippy = get_last_clippy(engine)
    subprocess.call(['notify-send', "%s -> %s" % (last_clippy['translation'], last_clippy['alternatives']), "--expire-time", "3000"])

def notify(engine, args):
    subprocess.call(['notify-send', args, "--expire-time", "3000"])

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
