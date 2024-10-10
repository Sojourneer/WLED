import json
from googletrans import Translator

key = "Back"
data = {}

translator = Translator()
keyt = translator.translate(key, src="en",dest="ja").text

data[key] = keyt
print(data)
with open("junk.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
