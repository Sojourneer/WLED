from bs4 import BeautifulSoup, Comment, Declaration
import sys
import shutil
import os
import re
import json
import hashlib
import argparse

parser = argparse.ArgumentParser(
                    prog='L12N',
                    description='Templatizes (HTML) files listed in I18N/data/list.json and outputs a phrase index'
)

parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

args = parser.parse_args()

fnI18N = 'wled00/I18N/data/I18N.json'
I18N = {}
if os.path.exists(fnI18N):
    with open(fnI18N, 'r') as file:
        I18N = json.load(file)
else:
        I18N = {}    

with open('wled00/I18N/data/list.json', 'r') as file:
    sourceFiles = json.load(file)

#nonWhitespace = re.compile("\S")
nonWhitespace = re.compile("\w")
allNumbers = re.compile("^[0-9]+$")

def ensureScript(soup,URL):
    for script in soup.find_all('script'):
        if script.string is not None: continue # inline script
        if script.get('src') == URL: return

    #add script
    head = soup.find('head')
    if head == None:
        head = soup.new_tag("head")
        soup.find("html").insert(0,head)
    script = soup.new_tag("script")
    script["src"] = URL
    head.append(script)

def ensureTemplateId(soup,id,content):
    entry = soup.find(id=id)
    if(entry):
        entry.string = content
        return
    entry = soup.new_tag("div")
    entry["id"] = id
    entry["style"] = "display:none"
    entry.string = content
    soup.find("body").append(entry)


# Currently, the prompt is not used, because there are too many placeholders.
def I18N_YN(str, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write("I18N for " + str + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def addClassI18N(tag):
    try:
        clist = tag.get('class', [])
        if not ("I18N" in clist):
            tag["class"] =  clist + ['I18N']
        return True
    finally:
        return False

def processFile(fn,tagfn,outfn):
    templateNameId = "I18N:template"
    global I18N
    if tagfn in I18N:
        json_section = I18N[tagfn]
    else:
        json_section = I18N[tagfn] = {}
    #print("JSON section", json_section)

    with open(fn) as html_file:
        #soup = BeautifulSoup(html_file.read(), features='html.parser')
        soup = BeautifulSoup(html_file.read(), features='html.parser')

        # Go through each tag with text and replace with placeholder
        i = 1
        for tag in soup.find_all(text=True):
            if tag.string == "html": continue
            if isinstance(tag, Declaration): continue
            if isinstance(tag, Comment): continue
            if tag.parent.name in ["script","style"]: continue

            if not nonWhitespace.search(tag.string): continue
            if allNumbers.match(tag.string): continue
            if tag.string[0:2] == "${": continue

            hash = hashlib.sha1(bytes(tag.string,'utf-8')).hexdigest()
            if args.verbose: print(tag.string,hash)
            if not hash in json_section:
                json_section[hash] = {"content":tag.string, "sourceLine": tag.parent.sourceline}
            
            #Handle special case of body being simply text, which messes up the appending of elements
            if tag.parent.name == "body" or len(tag.parent.contents) > 1:
                enclosure = soup.new_tag("span")
                enclosure.string = tag.string
                #tag.parent.append(enclosure)
                #tag.string.replace_with("")
                tag.replace_with(enclosure)
                tag = enclosure
            tag.string.replace_with("${{{0}:{1}}}".format(hash, tag.string))
            i += 1
            #addClassI18N(tag)
            #tag.parent["data-I18N"] = "text"

        dataList = None
        def templatizeAttribute(attrName,tag):
            nonlocal i, dataList
            if tag.has_attr(attrName) and tag[attrName][0:2] != "${":
                hash = hashlib.sha1(bytes(tag[attrName],'utf-8')).hexdigest()
                if args.verbose: print(tag[attrName],hash)
                if not hash in json_section:
                    json_section[hash] = {"attr":attrName, "value":tag[attrName], "sourceLine": tag.sourceline}
                tag[attrName] = "${{{0}:{1}}}".format(hash, tag[attrName])
                i += 1
                dataList.append(attrName)
                return True
            return False

        # Go through each tag looking for text in specific attributes and replace with placeholder
        for tag in soup.find_all():
            dataList = []
            isTarget = False
            isTarget |= templatizeAttribute("title", tag)
            isTarget |= templatizeAttribute("placeholder", tag)
            if isTarget:
                #addClassI18N(tag)
                tag["data-I18N"] = ",".join(dataList)

        # Infrastructure for templates
        ensureScript(soup,"../scripts/localize.js")
        ensureTemplateId(soup, templateNameId, tagfn)

        #new_text = soup.prettify()
        new_text = str(soup)

    # Write parameterized version
    with open(outfn, mode='w') as new_html_file:
        new_html_file.write(new_text)

for infn in sourceFiles:
    srcfn = infn

    print("PROCESSING",srcfn)
    templatefn = infn

    processFile(srcfn,infn,templatefn)

    # temporarily output after each file
    with open(fnI18N,'w') as f:
        json.dump(I18N, f, ensure_ascii=True, indent=4)

# the end