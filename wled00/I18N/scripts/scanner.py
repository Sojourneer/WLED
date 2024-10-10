from bs4 import BeautifulSoup, Comment, Declaration
import sys
import re
import json


with open('wled00/I18N/src/list.json', 'r') as file:
    sourceFiles = json.load(file)

#nonWhitespace = re.compile("\S")
nonWhitespace = re.compile("\w")
allNumbers = re.compile("^[0-9]+$")

i18n = {}


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

def processFile(fn,outfn):
    json_section = i18n[fn] = {}
    with open(fn) as html_file:
        #soup = BeautifulSoup(html_file.read(), features='html.parser')
        soup = BeautifulSoup(html_file.read(), features='html.parser')

        # Go through each 'A' tag and replace text with '-'
        for tag in soup.find_all(id='A'):
            tag.string.replace_with('-')
        i = 1
        for tag in soup.find_all(text=True):
            if tag.string == "html": continue
            if isinstance(tag, Declaration): continue
            if isinstance(tag, Comment): continue
            if tag.parent.name in ["script","style"]: continue

            if not nonWhitespace.search(tag.string): continue
            if allNumbers.match(tag.string): continue
            if tag.string[0:1] == "${": continue

            #if len(tag.string) == 1: print(ascii(tag.string[0]))
            #print(tag, tag.parent.sourceline, tag.parent.sourcepos)
            #continue

            #print("'" + tag.string + "'")
            #if(I18N_YN(tag.string)):
            if(True):
                json_section[i] = {"content":tag.string, "sourceLine": tag.parent.sourceline}
                tag.string.replace_with("${{{0}:{1}}}".format(i, tag.string))
                i += 1

        for tag in soup.find_all():
            if not tag.has_attr("title"): continue

            json_section[i] = {"title":tag["title"], "sourceLine": tag.sourceline}
            tag["title"] = "${{{0}:{1}}}".format(i, tag["title"])
            i += 1
            

        #new_text = soup.prettify()
        new_text = str(soup)

    # Write new contents to test.html
    with open(outfn, mode='w') as new_html_file:
        new_html_file.write(new_text)

for infn in sourceFiles:
    print("PROCESSING",infn)
    outfn = "wled00/I18N/src/data" + infn[len("wled00/data"):]
    #print(infn, outfn)
    processFile(infn,outfn)

    # temporarily output after each file
    with open('wled00/I18N/scripts/data.json','w') as f:
        json.dump(i18n, f, ensure_ascii=True, indent=4)

