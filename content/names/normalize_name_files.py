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
  Deduplicated names are written to newnames_R.json
  Merged names are written to newnames_M.json"""

    pretty_indent = 2
    inbound_encoding = "utf-8-sig"
    outbound_encoding = "utf-8"

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

    # Load new names from JSON to struct
    with newfn.open("r", encoding=inbound_encoding) as nfh:
        nj = json.load(nfh)

    nnraw = nj[0]["aValues"]
    nnames = hashmotize_raw_names(nnraw)
    print("New name list (raw) contains {} entries".format(len(nnames)))

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
