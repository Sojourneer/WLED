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

parser.add_argument('-l', '--lang', help='Two letter language code', type=LangFile, nargs='+', required=True)      # option that takes a value
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

args = parser.parse_args()

translator = Translator()

with open("wled00/I18N/data/I18N.json", "r") as f:
    raw = json.load(f)

def cookedKey(item):
    return item["text"]

flat = []
for fn in raw:
    fc = raw[fn]
    for hash in fc:
        spec = fc[hash]
        #print(fn, ndx, spec)
        if "content" in spec:
            type = "content"
            text = spec["content"]
        else:
            type = spec["attr"]
            text = spec["value"]
        flat.append({"key":hash, "fn":fn, "text": text, "sourceLine":spec["sourceLine"], "type": type})
flat1 = sorted(flat,key=cookedKey)
print(flat1)

def translate(target_lang):
    print("TRANSLATING INTO {}".format(target_lang))
    cooked = {}
    cnt = 0
    surroundWS = re.compile("(?s)^([\t\n ]*+)(.*[^\t\n ])([\t\n ]*)$")

    for text, instanceG in itertools.groupby(flat1, key=cookedKey):
        instanceL = list(instanceG)
        hash = instanceL[0]["key"]
        if target_lang == None:
            translation = "<TBD>"
        else:
            m = surroundWS.match(text)
            if m == None:
                print("Mismatch item {} '{}'".format(hash,text))
                translation = text
            else:
                translation = m.group(1) + translator.translate(m.group(2), sr="en", dest=target_lang).text + m.group(3)

        #{hash:{"text":text, "translation":{translation:{fn:[sourceLine ...], ...}]}
        fnEntries = {}
        for fn, fng in itertools.groupby(instanceL, key=lambda x: x["fn"]):
            fnL = list(fng)
            fnEntries[fn] = list(map(lambda x: int(x["sourceLine"]), fnL))
            #print(text, fn, list(map(lambda x: int(x["index"]), fng)))
        
        entry = {"text": text, "translations": [{"translation":translation, "for":fnEntries}]}
        cooked[hash] = entry
        cnt = cnt + 1
        if(cnt % 10) == 9: print(cnt)

    if target_lang == None:
        with open("wled00/I18N/L12N/L12N.json", "w") as f:
            json.dump(cooked, f, indent=4)
    else:
        with open("wled00/I18N/L12N/{0}.json".format(target_lang), "w", encoding="utf-8") as f:
            json.dump(cooked, f, indent=4, ensure_ascii=False)

for target_lang in args.lang:
    translate(target_lang)