from typing import *
import itertools
from plover.translation import Translator, Stroke, Translation
import os
# Convert the translations into strokes


def flatten(x: List[List]) -> List:
    return list(itertools.chain.from_iterable(x))

def retro_stroke(translator: Translator, stroke: Stroke, cmdline: str):
    all_translations = translator.get_state().translations
    affected_translation_cnt = len(list(
        itertools.takewhile(
            lambda x: x.strokes[-1] == stroke,
            reversed(all_translations)
        )
    ))
    affected_translations = all_translations[-(affected_translation_cnt + 1):]
    print(affected_translation_cnt, affected_translations)
    affected_strokes = flatten([x.strokes for x in affected_translations])
    result = []
    for x in affected_translations:
        strokes = reversed(list(itertools.dropwhile(lambda x: x == stroke, reversed(x.strokes))))
        result.append('/'.join([y.rtfcre for y in strokes]))
    resulting_string = ' '.join(result)
    my_trans = Translation(affected_strokes + [stroke], resulting_string)
    my_trans.replaced = affected_translations

    translator.translate_translation(my_trans)


