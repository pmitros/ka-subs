'''
This script generates clean JSON files for use in our extension from
translated subtitles.

It puts Arabic text as Unicode, for ease of human editing, converts
Youtube-format to be the same as KA-format subtitles, etc.

Some of this stuff is redundant, since translate does it already, but
it is a quick hack.
'''

import json
import os


def pp(filename):
    print(filename)
    js = json.load(open(filename))
    if isinstance(js['data'], str):
        js['data'] = json.loads(js['data'])
    if isinstance(js['data'], dict):
        js['data'] = js['data']['events']
    for item in js['data']:
        if 'kaIsValid' in item:
            if item['kaIsValid'] != True:
                raise "Huh"
            item.pop('kaIsValid')
        if 'startTime' not in item:
            item['startTime'] = item['tStartMs']
            item['endTime'] = item['tStartMs'] + item['dDurationMs']
            del item['tStartMs']
            del item['dDurationMs']
        if 'segs' in item:
            if len(item['segs']) != 1:
                raise "Segs mismatch"
            del item['segs']
    if 'ts' in js:
        del js['ts']
    return json.dumps(js, indent=3, ensure_ascii=False)


for fn in os.listdir("."):
    if not fn.endswith(".trans"):
        continue
    with open(fn.replace(".trans", ".i18n"), "w", encoding='utf-8') as fp:
        fp.write(pp(fn))
