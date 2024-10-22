# Localization Proposal

## Client scope
1. Display language only, including text delivered to browser via JSON api (effects,palettes,...).  Date formats, etc. are not covered.
2. Display language is a property of the WLED instance.  Each browser client will use the same language.

## Translation features
1. Translation comprises an Internationalization step and a separate step of Translation for each language
2. Both Internationalization and Translation are incremental process, which allows a process of test-and-amend, as well as reuse of previous work on new builds.  This is facilitated by using a hash to identify each piece of internationalized text
3. The Internationalization process replaces target text in HTML files with placeholders referencing a hash of the original text.  The result is called a Templatized file.  Script that includes target text moves it to the including HTML in a hidden section.    

## Runtime structure
1. The display language is set in the xxxx settings page
2. WLED serves templatized files. The first script to run in any HTML page replaces the template's placeholders with translated text obtained from the translation dictionary.
3. The translation dictionary for the current display language is retrieved from a central repository (e.g. github), and cached in Window:localStorage. 
   1. Refetching can be forced in the xxx settings page. 
   2. This implies that github or other central repository must be available to each browser client device the first time it accesses WLED, whenever the display language is set, or when refetching is requested.