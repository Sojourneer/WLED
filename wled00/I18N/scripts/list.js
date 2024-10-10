const fs = require('fs');

function outputJSON(path,content) {
  try {
    fs.writeFileSync(path, JSON.stringify(content, null, 2), 'utf8');
    console.log('Data successfully saved');
  } catch (error) {
    console.log('An error has occurred ', error);
  }
}


files = []
function writeHtmlGzipped(fn,a,b)
{
    files.push(fn);
}

function writeChunks(dir, specs)
{
    for(i in specs) {
      spec = specs[i];
      //console.log(spec);
      files.push(dir + "/" + spec.file);
    }  
}

writeHtmlGzipped("wled00/data/index.htm", "wled00/html_ui.h", 'index');
writeHtmlGzipped("wled00/data/simple.htm", "wled00/html_simple.h", 'simple');
writeHtmlGzipped("wled00/data/pixart/pixart.htm", "wled00/html_pixart.h", 'pixart');
writeHtmlGzipped("wled00/data/cpal/cpal.htm", "wled00/html_cpal.h", 'cpal');
writeHtmlGzipped("wled00/data/pxmagic/pxmagic.htm", "wled00/html_pxmagic.h", 'pxmagic');

writeChunks(
  "wled00/data",
  [
    {
      file: "style.css",
      name: "PAGE_settingsCss",
      method: "gzip",
      filter: "css-minify",
      mangle: (str) =>
        str
          .replace("%%","%")
    },
    {
      file: "settings.htm",
      name: "PAGE_settings",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_wifi.htm",
      name: "PAGE_settings_wifi",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_leds.htm",
      name: "PAGE_settings_leds",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_dmx.htm",
      name: "PAGE_settings_dmx",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_ui.htm",
      name: "PAGE_settings_ui",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_sync.htm",
      name: "PAGE_settings_sync",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_time.htm",
      name: "PAGE_settings_time",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_sec.htm",
      name: "PAGE_settings_sec",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_um.htm",
      name: "PAGE_settings_um",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_2D.htm",
      name: "PAGE_settings_2D",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "settings_pin.htm",
      name: "PAGE_settings_pin",
      method: "gzip",
      filter: "html-minify"
    }
  ],
  "wled00/html_settings.h"
);

writeChunks(
  "wled00/data",
  [
    {
      file: "usermod.htm",
      name: "PAGE_usermod",
      method: "gzip",
      filter: "html-minify",
      mangle: (str) =>
        str.replace(/fetch\("http\:\/\/.*\/win/gms, 'fetch("/win'),
    },
    {
      file: "msg.htm",
      name: "PAGE_msg",
      prepend: "=====(",
      append: ")=====",
      method: "plaintext",
      filter: "html-minify",
      mangle: (str) => str.replace(/\<h2\>.*\<\/body\>/gms, "<h2>%MSG%</body>"),
    },
    {
      file: "dmxmap.htm",
      name: "PAGE_dmxmap",
      prepend: "=====(",
      append: ")=====",
      method: "plaintext",
      filter: "html-minify",
    },
    {
      file: "update.htm",
      name: "PAGE_update",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "welcome.htm",
      name: "PAGE_welcome",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "liveview.htm",
      name: "PAGE_liveview",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "liveviewws2D.htm",
      name: "PAGE_liveviewws2D",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "404.htm",
      name: "PAGE_404",
      method: "gzip",
      filter: "html-minify",
    },
    {
      file: "favicon.ico",
      name: "favicon",
      method: "binary",
    },
    {
      file: "iro.js",
      name: "iroJs",
      method: "gzip"
    },
    {
      file: "rangetouch.js",
      name: "rangetouchJs",
      method: "gzip"
    }
  ],
  "wled00/html_other.h"
);

outputJSON("wled00/I18N/src/list.json",files.filter(s => s.endsWith(".htm")));
