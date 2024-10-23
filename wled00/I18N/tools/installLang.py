# Optimizes content of I18N/L12N/<lang>.json for use by browser
import argparse
import json
import itertools
import os

parser = argparse.ArgumentParser(
                    prog='L12N',
                    description='Optimizes L12N/<lang>.json for use by browser'
)

def LangFile(la):
    if(len(la) != 2):
        raise argparse.ArgumentTypeError("Expecting 2 letter code!")
    if not os.path.exists("wled00/I18N/L12N/{}.json".format(la)):
        raise argparse.ArgumentTypeError("L12N/{}.json doesn't exist".format(la))
    return la

parser.add_argument('-l', '--lang', help='Two letter language code', type=LangFile, nargs='+', required=True)      # option that takes a value
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

args = parser.parse_args()

'''
    "3ff6d577a3dbf68bb7a695f124b57d351e53f937": {
        "text": "\n\t\t\t\tAnalog (PWM) and virtual LEDs cannot use automatic brightness limiter.",
        "translations": [{
            "translation": "\n\t\t\t\tアナログ (PWM) および仮想 LED は自動輝度リミッターを使用できません。",
            "for": {
                "wled00/data/settings_leds.htm": [
                    768
                ]
            }]
        }
    },
    h1: {
        "text": "text1",
        "translations": [
            {
                "translation": "tran1",
                "for": { .... }
            },
            {
                "translation": "tran2",
                "for": { f1: [ 5,6 ], f2:[7,8] }
            },
            {
                "translation": "tran3",
                "for": { f1: [ 1,4 ], f3:[7,8] }
            }
        ]
    },
    =>
    h1: {
        "d": tran1,
        "o": {
            f1: [tran3, tran3, trans2, tran2 ],
            f2: [tran2],
            f3: [tran3]
        }
    }
'''
for target_lang in args.lang:
    with open("wled00/I18N/L12N/{}.json".format(target_lang), "r") as f:
        L12N = json.load(f)

    optimized = {}
    for hash in L12N:
        entry = L12N[hash]
        translationEntries = entry["translations"]
        if len(translationEntries) == 1:
            optimized[hash] = translationEntries[0]["translation"]
        else:
            # flatten it out to {"t":translation,"fn":fn, "line":l}
            # group by fn.
            # get the translations in order for that fn
            flat = []
            for t in translationEntries:    # {'translation': 'tran1', 'for': {'f1': [3, 1], 'f2': [1, 4]}}
                #print(t)
                for fn in t["for"]: # 'f1'
                    #print(fn)
                    fnE = t["for"][fn] # [3, 1]
                    for line in t["for"][fn]:
                        flat.append({"t": t["translation"], "fn":fn, "line":line})
            
            overrides = {}
            flat = sorted(flat, key=lambda fe: fe["fn"])
            for fn, fnG in itertools.groupby(flat, key=lambda fe: fe["fn"]):
                # Now we need to sort the translations by line
                sortedTrans = sorted(list(fnG), key=lambda fe: fe["line"])
                sortedTranslations = list(map(lambda fe: fe["t"], sortedTrans))
                if len(set(sortedTranslations)) == 1:
                    overrides[fn] = sortedTranslations[0]
                else:
                    overrides[fn] = sortedTranslations
           
            optimized[hash] = overrides

    with open("wled00/I18N/langs/{0}.json".format(target_lang), "w", encoding="utf-8") as f:
        json.dump(optimized, f, indent=4, ensure_ascii=False)