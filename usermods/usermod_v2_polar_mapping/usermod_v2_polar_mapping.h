#pragma once

#include "wled.h"

void dumpJsonObject(JsonObject obj);

class PolarMapping;
PolarMapping *_mapper;

uint16_t polar_radial_chase(uint32_t color1, uint32_t color2);
uint16_t polar_angular_chase(uint32_t color1, uint32_t color2);

uint16_t mode_polar_radial_chase(void) {
  _mapper = (PolarMapping *)usermods.lookup(USERMOD_ID_POLAR_MAPPING);

  return polar_radial_chase(SEGCOLOR(0), SEGCOLOR(1));
}

uint16_t mode_polar_angular_chase(void) {
  return polar_angular_chase(SEGCOLOR(0), SEGCOLOR(1));
}

#define PALETTE_SOLID_WRAP   (strip.paletteBlend == 1 || strip.paletteBlend == 3)

static const char _data_FX_MODE_POLAR_RADIAL[] PROGMEM =   "Polar Radial Chase@!,Width,,,,Reverse;!,!;!;!;1";
static const char _data_FX_MODE_POLAR_ANGULAR[] PROGMEM = "Polar Angular Chase@!,Width,,,,Reverse;!,!,!;!;!;1";


class PolarMapping : public Usermod {
  private:
     // string that are used multiple time (this will save some flash memory)
    static const char _name[];

    // any private methods should go here (non-inline method should be defined out of class)
    int split(String s); 

  public:
    String       _counts;
    int         _mapping[10];
    int         _totalCount;
    int         _maxRing;

    // non WLED related methods, may be used for data exchange between usermods (non-inline methods should be defined out of class)
    int PolarToIndex(uint8_t r, uint16_t a /*, JsonObject& result*/);
    void IndexToPolar(uint16_t index, uint8_t& r, uint16_t& a);

    // methods called by WLED (can be inlined as they are called only once but if you call them explicitly define them out of class)

    void setup() {
      _mapper = this;

      strip.addEffect(255, &mode_polar_radial_chase, _data_FX_MODE_POLAR_RADIAL);     //FX_MODE_POLAR_RADIAL
      strip.addEffect(255, &mode_polar_angular_chase, _data_FX_MODE_POLAR_ANGULAR);   //FX_MODE_POLAR_ANGULAR

      DEBUG_PRINTLN(F("PolarMapping::setup()"));
    }

    void connected() { /* no action */}

    void loop() { /* no action */ }

    /*
     * Called after usermod setting changes.
     * Takes the usermod instance's state and copies it into the cfg json, making it available to edit.
     */
    void addToConfig(JsonObject& root)
    {
      JsonObject usermod = root[FPSTR(_name)];
      DEBUG_PRINTF("PM atc: usermod %s.  _maxRing %d\n", usermod.isNull() ? "null" : "not-null", _maxRing);

      if(usermod.isNull())
        usermod = root.createNestedObject(FPSTR(_name));

      JsonObject config = usermod.createNestedObject("map");
      if(config.isNull())
        config = usermod.createNestedObject("map");

      if(config["counts"].isNull())
        config["counts"] = _counts;

    }


    /*
     * readFromConfig() can be used to read back the custom settings you added with addToConfig().
     * This is called by WLED when settings are loaded (currently this only happens immediately after boot, or after saving on the Usermod Settings page)
     * 
     * readFromConfig() is called BEFORE setup(). This means you can use your persistent values in setup() (e.g. pin assignments, buffer sizes),
     * but also that if you want to write persistent values to a dynamic buffer, you'd need to allocate it here instead of in setup.
     * If you don't know what that is, don't fret. It most likely doesn't affect your use case :)
     * 
     * Return true in case the config values returned from Usermod Settings were complete, or false if you'd like WLED to save your defaults to disk (so any missing values are editable in Usermod Settings)
     * 
     * getJsonValue() returns false if the value is missing, or copies the value into the variable provided and returns true if the value is present
     * The configComplete variable is true only if the "exampleUsermod" object and all values are present.  If any values are missing, WLED will know to call addToConfig() to save them
     * 
     * This function is guaranteed to be called on boot, but could also be called every time settings are updated
     */
    bool readFromConfig(JsonObject& root)
    {
      // default settings values could be set here (or below using the 3-argument getJsonValue()) instead of in the class definition or constructor
      // setting them inside readFromConfig() is slightly more robust, handling the rare but plausible use case of single value being missing after boot (e.g. if the cfg.json was manually edited and a value was removed)
      DEBUG_PRINTF("PM. has um %d, has usermod=%d\n", root.containsKey("um"), root.containsKey(FPSTR(_name)));
      // serializeJson(root, DEBUGOUT); // crashes the program
      dumpJsonObject(root);
 
      JsonObject usermod = root[FPSTR(_name)];
      DEBUG_PRINTF("PM rfc: usermod %s.  _maxRing %d\n", usermod.isNull() ? "null" : "not-null", _maxRing);


      bool configComplete = !usermod.isNull();
      //String counts; 

      DEBUG_PRINTLN(usermod["map"]["counts"].as<String>());
      configComplete &= getJsonValue(usermod["map"]["counts"], _counts);
      DEBUG_PRINT("PM::readFromConfig@counts:");
      DEBUG_PRINTLN(_counts);

      _maxRing = split(_counts);
      DEBUG_PRINTF("maxRing=%d\n", _maxRing);

      return true; //configComplete;
    }

    /*
     * getId() allows you to optionally give your V2 usermod an unique ID (please define it in const.h!).
     * This could be used in the future for the system to determine whether your usermod is installed.
     */
    uint16_t getId()
    {
      return USERMOD_ID_POLAR_MAPPING;
    }

};


// add more strings here to reduce flash memory usage
const char PolarMapping::_name[]    PROGMEM = "PolarMapping";

// implementation of non-inline member methods
int  PolarMapping::PolarToIndex(uint8_t r, uint16_t a /*, JsonObject& result*/)
{
    int index = 0, i;
    for(i=0; i < r; ++i) {
        index += _mapping[i];
    }
    double increment = 360.0 / (float) _mapping[r];
    index += (int)round(a/increment) % _mapping[r];

    //result["indices"].add(index);

    return index;
}

void PolarMapping::IndexToPolar(uint16_t index, uint8_t& r, uint16_t& a)
{
    r = 0;
    a = 0;
    while(index > _mapping[r]) {
      index -= _mapping[r];
      r++;
    }

    double increment = 360.0 / (float) _mapping[r];
    index += (int)round(a/increment) % _mapping[r];
    a = increment * index;
}

int PolarMapping::split(String s) {
  int from = 0;
  uint8_t n = 0;
  int index;
  _totalCount = 0;
  int cnt;
  while((index = s.indexOf(",",from)) != -1) {
    _mapping[n++] = cnt = s.substring(from, index).toInt();
    from = index+1;
    _totalCount += cnt;
  }

  _mapping[n] = cnt = s.substring(from).toInt();
  _totalCount += cnt;

  return n;
}

// ---- THE EFFECTS ----

uint16_t polar_angular_chase(uint32_t color1, uint32_t color2) { // chase theta
  bool reverse = SEGMENT.check1;

  //uint8_t width = 1;
  uint32_t cycleTime = 50 + (255 - SEGMENT.speed);
  uint32_t it = strip.now / cycleTime;
  bool usePalette = color1 == SEGCOLOR(0);
  
  if(SEGENV.call == 0)
    SEGENV.aux0 = 0; 

  for (int i = 0; i < SEGLEN; i++) {
    SEGMENT.setPixelColor(i,color2);
  }

  int angleIncrement = _mapper->_mapping[0];
  int maxRing = _mapper->_maxRing;
  

  for (uint8_t r = 0; r <= maxRing; r++) {
    int i;
    if (usePalette) color1 = SEGMENT.color_from_palette(r, true, PALETTE_SOLID_WRAP, 0);
    i = _mapper->PolarToIndex(r, SEGENV.aux0 /*, result*/);

    if(i >= 0 && i < SEGLEN) {
      SEGMENT.setPixelColor(i,color1);
    }
  }

  if (it != SEGENV.step) {
    SEGENV.aux0 = (SEGENV.aux0 + (360.0 / angleIncrement));
    if(SEGENV.aux0 >= 360.0) SEGENV.aux0 = 0;

    SEGENV.step = it;
  }

  return FRAMETIME;
}

uint16_t polar_radial_chase(uint32_t color1, uint32_t color2) { // chase r
  //uint8_t width = 1;
  uint32_t cycleTime = 50 + (255 - SEGMENT.speed);
  uint32_t it = strip.now / cycleTime;
  bool usePalette = color1 == SEGCOLOR(0);
  
  if(SEGENV.call == 0)
    SEGENV.aux1 = 0; 
  
  uint8_t r;
  uint16_t a;
  for (int i = 0; i < SEGLEN; i++) {
    _mapper->IndexToPolar(i, r, a);
    //uint16_t pcolor = SEGENV.aux1;
    uint16_t pcolor = a; 
    //uint16_t pcolor = (uint16_t)(a/30); 
    if (usePalette) color2 = SEGMENT.color_from_palette(pcolor, true, PALETTE_SOLID_WRAP, 2);
    SEGMENT.setPixelColor(i,color2);
  }

  //int radialIncrement = 1;
  int maxRing = _mapper->_maxRing;
  
  int fromIndex, uptoIndex;
  fromIndex = _mapper->PolarToIndex(SEGENV.aux1, 0); 
  uptoIndex = (SEGENV.aux1 < maxRing) ? _mapper->PolarToIndex(SEGENV.aux1+1, 0) : _mapper->_totalCount; 

  for (int i=fromIndex; i < uptoIndex; ++i) {
    if (usePalette) color1 = SEGMENT.color_from_palette(SEGENV.aux1*5+40, true, PALETTE_SOLID_WRAP, 2);
    if(i >= 0 && i < SEGLEN) {
      SEGMENT.setPixelColor(i,color1);
    }
  }

  if (it != SEGENV.step) {
    SEGENV.aux1 += 1;
    if(SEGENV.aux1 > maxRing) SEGENV.aux1 = 0;

    SEGENV.step = it;
  }

  return FRAMETIME;
}

void dumpJsonObject(JsonObject obj) {
  for (JsonPair kv : obj) {
      Serial.println(kv.key().c_str());
      Serial.println(kv.value().as<const char*>());
  }
}
