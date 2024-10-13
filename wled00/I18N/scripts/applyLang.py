# get lang from CLI
# load the lang json file, and reshape for single pass thru files
# for each file, apply the template

import argparse
import json
from bs4 import BeautifulSoup, Comment, Declaration
import re
import os

parser = argparse.ArgumentParser(
                    prog='applyLang',
                    description='Applies localization file for specified language to WLED UI src, prior to rebuilding'
)

def LangFile(la):
    if(len(la) != 2):
        raise argparse.ArgumentTypeError("Expecting 2 letter code!")
    fn = "wled00/I18N/langs/{}.json".format(la)
    print(fn)
    if(os.path.isfile(fn) == False):
        raise argparse.ArgumentTypeError("Language file {} not found".format(fn))
    return fn

parser.add_argument('-l', '--lang', help='Two letter language code', type=LangFile, required=True)      # option that takes a value
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

args = parser.parse_args()
#print(args)

with open(args.lang, "r") as f:
    raw = json.load(f)

# Reshape to file: {id:trans}
byFn = {}
for phrase in raw:
    phraseEntry = raw[phrase]
    for translation in phraseEntry:
        translationEntry = phraseEntry[translation]
        for fn in translationEntry:
            instances = translationEntry[fn]
            #print(phrase,translation,instances)
            if not (fn in byFn): byFn[fn] = {} #{'entries':[]}
            fnEntry = byFn[fn]
            for n in instances:
                #fnEntry['entries'].append({n:translation})
                if n in fnEntry:
                    raise Exception("Duplicate entry {} in {}".format(n,fn))
                fnEntry[n] = translation

# Since we could have missing entries, for robustness we will use dictionary lookup
variable = re.compile("\\$\\{([0-9]+):[^\\}]*\\}")

for fn in byFn:
    fnTemplate = "wled00/I18N/src/data" + fn[len("wled00/data"):]
    fnOutput =   fn
    fnEntry = byFn[fn]
    if(args.verbose): print("Processing file {}".format(fn),fnEntry)

    with open(fnTemplate) as html_file:
        soup = BeautifulSoup(html_file.read(), features='html.parser')
        
        for tag in soup.find_all(text=True):
            #print("Text", tag.string)
            m = variable.match(tag.string)
            if not m is None:
                var = int(m.group(1))
                if var in fnEntry:
                    if(args.verbose): print(tag.string,fnEntry[var],tag.parent.sourceline)
                    tag.string.replace_with(fnEntry[var])
                else:
                    print("in {} missing entry for variable {}".format(fnTemplate,var))
        
        for tag in soup.find_all():
            if not tag.has_attr("title"): continue

            m = variable.match(tag["title"])
            if not m is None:
                var = int(m.group(1))
                if var in fnEntry:
                    if(args.verbose): print(tag["title"],fnEntry[var])
                    tag["title"] = fnEntry[var]
                else:
                    print("in {} missing entry for variable {}".format(fnTemplate,var))

    new_text = str(soup)
    print("Template",fnTemplate,"Output",fn)

    # Write localized version
    with open(fnOutput, mode='w') as new_html_file:
        new_html_file.write(new_text) 
