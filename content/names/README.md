# Expanded Character Name Files

## Format of `names_first.json`

The basic format of the data faile containing first names is:

```json
[
  {
    "strName" : "First Names",
    "aValues" : [
      "Aaliyah","IsFemale",
      "Aaron","IsMale",
      "Abby","IsFemale",
      "Abigail","IsFemale",
      "Abisoye","IsNB",
      "Abraham","IsMale",
      "Zhen","IsFemale",
      "Zoe","IsFemale",
      "Zoey","IsFemale"
   ]
  }
]
```

Note that all names and their gender associations are stored as a single list not as pairs. In `jq` query form, odd elements are names and even elements are gender associations. For example (forgive the weird Windows quoting):

```
$ cat names_first.json | jq ".[0][\"aValues\"][0]"
"Aaliyah"

$ cat names_first.json | jq ".[0][\"aValues\"][1]"
"IsFemale"
```

Also, the original `names_first.json` file contains three high-bit characters before the expected `[`:

```
$ xxd names_first.json | head -n 6
00000000: efbb bf5b 0d0a 2020 7b0d 0a20 2020 2022  ...[..  {..    "
00000010: 7374 724e 616d 6522 203a 2022 4669 7273  strName" : "Firs
00000020: 7420 4e61 6d65 7322 2c0d 0a20 2020 2022  t Names",..    "
00000030: 6156 616c 7565 7322 203a 205b 0d0a 2020  aValues" : [..
00000040: 2020 2020 2241 616c 6979 6168 222c 2249      "Aaliyah","I
00000050: 7346 656d 616c 6522 2c0d 0a20 2020 2020  sFemale",..
```

~~The purpose of the~~ __The initial__ `0xEF 0xBB 0xBF` ~~is unknown but it~~ __is a UTF-8 *Byte Order Mark* (BOM) which__ can cause issues when attempting to read the file. In particular, Python's `json` module throws errors unless these characters are removed __or the file is read with encoding set to `utf-8-sig`__

See the `normalize_name_files.py` for a commented example/proof-of-concept script which reads, alters, and writes JSON name files. This script deduplicates and merges two JSON first name files and writes the results to two new files. The script also converts a two column CSV file containing _(name,gender)_ pairs to JSON format and performs the same deduplication and merging.

Otherwise, `names_first.json` has a very straightforward organization that should be reasonably simple to extend.

## Example: Nigerian Given Names

Additional character first names were taken from the 1000 most popular first names in Nigeria (https://forebears.io/nigeria/forenames). In cases where names were associated with a gender at least 90% of the time, the name was associated exclusively with that gender (*IsMale* or *IsFemale*). In the remaining cases, the name is marked as *IsNB*.

Raw name data is stored in a LibreOffice spreadsheet (`names_first_nigerian.ods`) and gender was manually copied over from the original web page.

The complete name list is stored in frequency order in `names_first_nigerian.json`. `base_name_filter.txt` is the list of names in `names_first_nigerian.json` which already exist in `C:\Program Files (x86)\Steam\SteamApps\common\Ostranauts\Ostranauts_Data\StreamingAssets\data\names_first.json`. `names_first_nigerian_reduced.json` contains only the names which are not already in `names_first.json`, also in frequency order. `names_first_nigerian_reduced_sorted.json` is the reduced name list sorted alphabetically.

Nigerian names in particular were selected to be consistent with game lore. The process used to generate these data files should be suitable for adding names from other regions.

### Editorial Issues

There may be errors in the transcribed data and the gender consolidation fraction of 90% was arbitrarily selected. The data was taken as-is from the original web page and was only filtered for uniqueness against the default `names_first.json`. Some names may be considered problematic in particular cultures.

It is suggested that the original web page, spreadsheet, and JSON files are reviewed before use.

## Example: Kazakh Given Names

Additional character first names were taken from the 1000 most popular first names in Kazakhstan (https://forebears.io/kazakhstan/forenames). Gender association was performed as for Nigerian names.

Raw name data is stored in a LibreOffice spreadsheet (`names_first_kazakh.ods`) and gender was manually copied over from the original web page.

The name/gender pairs were exported as a two column CSV file (`names_first_kazakh.csv`) in frequency order. The CSV data was converted to JSON (saved in `names_first_kazakh.json`) using `normalize_name_files.py`. `names_first_kazakh_R.json` contains only the names which are not already in `C:\Program Files (x86)\Steam\SteamApps\common\Ostranauts\Ostranauts_Data\StreamingAssets\data\names_first.json`. `names_first_kazakh_M.json` combines the reduced name list `names_first_kazakh_R.json` with the default names in `names_first.json`.

### Editorial Issues

There may be errors in the transcribed data and the gender consolidation fraction of 90% was arbitrarily selected. The data was taken as-is from the original web page; names with less than 3 characters were discarded as were those with no gender association (the data seemed suspect) and was filtered for uniqueness against the default `names_first.json`.

Again, it is suggested that the original web page, spreadsheet, and JSON files are reviewed before use.
