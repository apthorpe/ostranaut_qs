import csv
import json
from pathlib import Path
import sys

def grouped(iterable, n):
    """Return n per iteration for a given iterable"""
    return zip(*[iter(iterable)]*n)

def hashmotize_raw_names(raw_names):
    """ Given a flattened list of (name,gender) tuples, return a dict
    with names as keys and gender as values"""

    namedict = dict()
    for kk, vv in grouped(raw_names, 2):
        namedict[kk] = vv

    return namedict

def main():
    """Main name file analyzer and deduplicator"""
    usagemsg = \
"""Usage: normalize_name_files.py newnames.json defaultnames.json
      normalize_name_files.py newnames.csv defaultnames.json
  If new names stored as CSV, names are converted to JSON
  and written to newnames.json
  Deduplicated names are written to newnames_R.json (reduced name list)
  Merged names are written to newnames_M.json"""

    pretty_indent = 2
    inbound_encoding = "utf-8-sig"
    outbound_encoding = "utf-8"
    known_genders = ("IsMale", "IsFemale", "IsNB")
    min_name_length = 3

    nargs = len(sys.argv)

    if nargs < 3:
        if nargs > 1:
            # Throw error if too few arguments
            print("Error: Expected exactly two arguments")
        # Print usage and halt
        print(usagemsg)
        return

    # Get namefiles directly from sys.argv
    newfn = Path(sys.argv[1])
    deffn = Path(sys.argv[2])

    # Error and halt if both name files are not actually files
    if not (newfn.is_file() and deffn.is_file()):
        print("Error: Cannot find one or more input files")
        print(usagemsg)
        return

    # These should not throw exceptions; guarded by is_file() check
    newfn = newfn.resolve()
    deffn = deffn.resolve()

    # Print full path of input files
    print(f"New name file:     {newfn}")
    print(f"Default name file: {deffn}")

    # Load default names from JSON to struct
    # Note: the `encoding="utf-8-sig"` avoids errors when reading
    # UTF-8 JSON files which contain a Byte Order Mark (BOM)
    # before the JSON data. This has no effect on ASCII or UTF-8
    # encoded files without a BOM
    with deffn.open("r", encoding=inbound_encoding) as dfh:
        dj = json.load(dfh)

    dnraw = dj[0]["aValues"]
    dnames = hashmotize_raw_names(dnraw)
    print("Default name list (raw) contains {} entries".format(len(dnames)))

    # Load new names from JSON or CSV to struct
    nnraw = list()
    nj = list()
    nnames = dict()

    if newfn.suffix == ".json":
        # Load new names from JSON to struct
        with newfn.open("r", encoding=inbound_encoding) as nfh:
            nj = json.load(nfh)

        nnraw = nj[0]["aValues"]
        nnames = hashmotize_raw_names(nnraw)
        print("New name list (raw) contains {} entries".format(len(nnames)))
    elif newfn.suffix == ".csv":
        # Populate nnraw, nj, and nnames with CSV data; write nj struct as JSON
        nj.append({
            "strName": "First Names",
            "aValues": list()
        })
        # Load new names from CSV to struct
        with newfn.open("r") as nfh:
            namereader = csv.reader(nfh)
            for row in namereader:
                if row[0].startswith("#"):
                    print("INFO: Skipping commented row starting with {}".format(row[0]))
                else:
                    if len(row) >= 2:
                        # Ignore header/comment lines and too-short rows
                        name = row[0].strip()
                        gender = row[1].strip()
                        if len(name) >= min_name_length and gender in known_genders:
                            # Ignore too-short names and unrecognized gender
                            nnames[name] = gender
                        else:
                            print("INFO: Name too short ({}) or unrecognized gender ({})".format(name, gender))
                    else:
                        print("INFO: Row too short ({} < 2)".format(len(row)))

        # Fill arrays from dict
        for name in sorted(nnames.keys()):
            nnraw.append(name)
            nnraw.append(nnames[name])

        nj[0]["aValues"] = nnraw

        # Write CSV data as JSON
        newjfn = Path(str(newfn).replace(".csv", ".json"))
        if newjfn.exists():
            print("Warning: Will not overwrite existing {} with CSV data from {}".format(newjfn.name, newfn.name))
        else:
            print("Writing full CSV namelist to {}".format(newjfn))
            with newjfn.open("w", encoding=outbound_encoding) as rfh:
                json.dump(nj, rfh, indent=pretty_indent)
        newfn = newjfn

    # Assert: nnraw, nnames, and nj are all populated, either from JSON or CSV
    # Assert: newfn points at JSON file

    # Write reduced and merged name files

    # Remove new names which collide with default names
    for oldname in dnames:
        if oldname in nnames:
            nnames.pop(oldname, None)
            print(f"Removed duplicate name: {oldname}")

    # Modify nj in place to contain the deduplicated name list
    nj[0]["aValues"] = list()

    for name, gender in nnames.items():
        nj[0]["aValues"].append(name)
        nj[0]["aValues"].append(gender)
        # Modify dj in place to contain the deduplicated name list
        dj[0]["aValues"].append(name)
        dj[0]["aValues"].append(gender)

    # Write modified nj to <new_base>_reduced.json
    reduced_fn = str(newfn).replace(".json", "_R.json")
    reduced_fn = Path(reduced_fn)

    if reduced_fn.exists():
        print("Warning: Will not overwrite existing reduced file {}".format(reduced_fn))
    else:
        if str(reduced_fn) == str(newfn):
            print("Warning: Will not overwrite existing file {}".format(reduced_fn))
        else:
            print("Writing reduced new namelist to {} (unsorted)".format(reduced_fn))
            with reduced_fn.open("w", encoding=outbound_encoding) as rfh:
                json.dump(nj, rfh, indent=pretty_indent)

    # Write modified dj to <new_base>_merged.json
    merged_fn = str(newfn).replace(".json", "_M.json")
    merged_fn = Path(merged_fn)

    if merged_fn.exists():
        print("Warning: Will not overwrite existing merged file {}".format(merged_fn))
    else:
        if str(merged_fn) == str(newfn):
            print("Warning: Will not overwrite existing file {}".format(merged_fn))
        else:
            print("Writing merged new namelist to {} (unsorted)".format(merged_fn))
            with merged_fn.open("w", encoding=outbound_encoding) as mfh:
                json.dump(dj, mfh, indent=pretty_indent)

    return

main()
