'''
This script uses AWS Translate to convert subtitles from English to
Polish and Arabic. We only need one of those, but two is better for
making sure everything works.

The output is a bit ugly, but we'll clean it up with
pretty_print.py. I didn't want to debug or do much work in this script,
since running it costs AWS fees.
'''

import os
import os.path
import boto3
import json


translator = boto3.client(service_name='translate')

targets = ['pl', 'ar']


def i18n(segment):
    if 'segs' in segment:
        if len(segment['segs'][0]) != 1:
            raise "Error"
        segment['text'] = {
            'en': segment['segs'][0]['utf8']
        }
    if isinstance(segment['text'], str):
        segment['text'] = {
            'en': segment['text']
        }

    for target in targets:
        if target not in segment['text']:
            segment['text'][target] = translator.translate_text(
                Text=segment['text']['en'],
                SourceLanguageCode="en",
                TargetLanguageCode=target)['TranslatedText']
    return segment


for fn in os.listdir("."):
    print(fn)
    if not fn.endswith(".json"):
        print("Not JSON")
        continue
    if os.path.exists(fn+".trans"):
        print("Output exists")
        continue
    payload = json.load(open(fn))
    payload['data'] = json.loads(payload['data'].replace("\\n", " "))
    print(fn)
    if isinstance(payload['data'], dict):  # YouTube
        payload['data'] = payload['data']['events']

    if isinstance(payload['data'], list):  # Khan Academy
        for segment in payload['data']:
            print(".")
            i18n(segment)
    with open(fn+".trans", "w") as fp:
        fp.write(json.dumps(payload))
