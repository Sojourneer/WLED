from bs4 import BeautifulSoup
import re
import json

#
# How do we enumerate the src files.  And which src files?
#
#

nonWhitespace = re.compile("\S")

i18n = {}

def processFile(fn,outfn):
    json_section = i18n[fn] = {}
    with open(fn) as html_file:
        #soup = BeautifulSoup(html_file.read(), features='html.parser')
        soup = BeautifulSoup(html_file.read(), features='lxml')

        # Go through each 'A' tag and replace text with '-'
        for tag in soup.find_all(id='A'):
            tag.string.replace_with('-')
        i = 1
        for tag in soup.find_all(text=True):
            if(nonWhitespace.search(tag.string)):
                print("'" + tag.string + "'")
                json_section[i] = tag.string
                tag.string.replace_with("${{{0}}}".format(i))
                i += 1

        # Store prettified version of modified html
        #new_text = soup.prettify()
        new_text = str(soup)

    # Write new contents to test.html
    with open(outfn, mode='w') as new_html_file:
        new_html_file.write(new_text)

processFile('test.html','test-out.html')

with open('data.json','w') as f:
    json.dump(i18n, f, ensure_ascii=True, indent=4)