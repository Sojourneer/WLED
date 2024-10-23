alert("loaded")
var templateName;

var translation;
function getTranslation(callback)
{
    fetch("../I18N/langs/ja.json")
    .then((res) => res.text())
    .then((text) => {
        // do something with "text"
        console.log("text",text);
        translation = JSON.parse(text);
        callback();
    })
    .catch((e) => console.error(e));
}

function DoIt() {
    Localize();
    alert("Ready to do other initialization");
}

function TranslateText(placeholder) {
    const re = /([0-9a-f]+)/
    m = placeholder.match(re)
    if(m) {
        key = m[1]
        entry = translation[key]
        return entry;
    }
}

function Localize()
{
    templateName = document.getElementById("I18N:template").innerText;
    console.log(templateName);

    /*
    document.querySelectorAll(".I18N").forEach(function(e){
        console.log(e.innerText);
    });
    */

    const allElements = document.querySelectorAll("*");
    let textElements = [];
    allElements.forEach((ele) => (
        ((ele.textContent != undefined && ele.textContent.startsWith("${"))
        || ele.hasAttribute('data-I18N')
        )    && textElements.push(ele) )); 

    // Now do the translation
    for(i=0; i < textElements.length; ++i) {
        e = textElements[i];
        if(e.textContent.startsWith("${")) {
            e.textContent = TranslateText(e.textContent);
        }
        if(e.hasAttribute('data-I18N')) {
            attrNames = e.attributes['data-I18N'].value.split(",")
            console.log("attributes",attrNames)
            for(ia=0; ia < attrNames.length; ++ia)
                attrName = attrNames[ia];
                attr = e.attributes[attrName];
                attr.value = TranslateText(attr.value)
                console.log(attr, attrName, attr.value);
        }
        console.log(e,e.textContent, e.hasAttribute("data-I18N"));
    }
    return;
}

getTranslation(DoIt);
