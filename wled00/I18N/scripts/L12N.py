import argparse

import json
from googletrans import Translator
import itertools
import re

parser = argparse.ArgumentParser(
                    prog='L12N',
                    description='Creates translated phrase file for specified language from data.json'
)

def LangFile(la):
    if(len(la) != 2):
        raise argparse.ArgumentTypeError("Expecting 2 letter code!")
    return la

parser.add_argument('-l', '--lang', help='Two letter language code', type=LangFile, required=True)      # option that takes a value
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

args = parser.parse_args()

target_lang = args.lang
translator = Translator()

with open("wled00/I18N/scripts/data.json", "r") as f:
    raw = json.load(f)

def cookedKey(item):
    return item["text"]

flat = []
for fn in raw:
    fc = raw[fn]
    for ndx in fc:
        spec = fc[ndx]
        #print(fn, ndx, spec)
        if "content" in spec:
            type = "content"
            text = spec["content"]
        else:
            type = "title"
            text = spec["title"]
        flat.append({"text": text, "fn":fn, "index":ndx, "type": type})
flat1 = sorted(flat,key=cookedKey)
#print(cooked1)

cooked = {}
cnt = 0
surroundWS = re.compile("(?s)^([\t\n ]*+)(.*[^\t\n ])([\t\n ]*)$")

for text, textg in itertools.groupby(flat1, key=cookedKey):
    if target_lang == None:
        translation = "<TBD>"
    else:
        m = surroundWS.match(text)
        if m == None:
            print("Mismatch '{}'".format(text))
            translation = text
        else:
            translation = m.group(1) + translator.translate(m.group(2), sr="en", dest=target_lang).text + m.group(3)

    entry = {}
    entry2 = {}
    entry[translation] = entry2
    for fn, fng in itertools.groupby(textg, key=lambda x: x["fn"]):
        entry2[fn] = list(map(lambda x: int(x["index"]), fng))
        #print(text, fn, list(map(lambda x: int(x["index"]), fng)))
    cooked[text] = entry
    cnt = cnt + 1
    if(cnt % 10) == 9: print(cnt)

#print(cooked)
#exit(0)

if target_lang == None:
    with open("wled00/I18N/scripts/L12N.json", "w") as f:
        json.dump(cooked, f, indent=4)
else:
    with open("wled00/I18N/langs/{0}.json".format(target_lang), "w", encoding="utf-8") as f:
        json.dump(cooked, f, indent=4, ensure_ascii=False)

