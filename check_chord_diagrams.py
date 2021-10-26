from pathlib import Path
import re

import click
import click_pathlib


@click.command("Check that diagrams are listed for all used song chords.")
@click.option(
    "-i",
    "--song-dir",
    required=True,
    type=click_pathlib.Path(exists=True),
    help="input directory with songs",
)
def main(song_dir: Path) -> None:
    num_warn_files = 0
    for song_filename in song_dir.glob("*.tex"):
        song_file_str = song_filename.read_text()
        warn_message = check_file(song_file_str)
        if warn_message:
            num_warn_files += 1
            print(song_filename)
            print(warn_message)

    if num_warn_files == 0:
        print("All checks OK.")
    else:
        print(f"Warnings in {num_warn_files} song files.")


def check_file(song_file_str: str) -> str:
    """
    Checks if chord diagrams match the chords used in the song.
    """
    # Preprocess
    # Remove lines starting with '%'. Replace '\#' with 'sharp'.
    tex_code = song_file_str
    tex_code = "\n".join([s for s in tex_code.split("\n") if not s.startswith("%")])
    tex_code = tex_code.replace("\\#", "sharp")

    # Match everything between curly brackets in \ukechord{...} up until "_".
    diagrams = re.findall(
        r"\\ukechord\{([^\}_]+)[^\}]*\}",
        tex_code,
        re.DOTALL | re.UNICODE,
    )
    # Remove consecutive duplicates
    diagrams = [
        x for i, x in enumerate(diagrams)
        if i == len(diagrams) - 1 or x != diagrams[i + 1]
    ]
    diagrams_sort = sorted(diagrams, key=chord_sort_key)

    # Between curly brackets in \ch{...}, take all alphanum characters from
    # the beginning, after an optional star. This is to exclude \rep, \beats
    # or other special instructions inside. 
    used_chords = re.findall(
        r"\\ch\{\*?([\w\./]+)[^\}]*\}",
        tex_code,
        re.DOTALL | re.UNICODE,
    )
    # Sort and make unique. Remove "N.C."
    used_chords_uniq_sort = sorted(
        list(set(used_chords) - set(["N.C."])), key=chord_sort_key
    )
    used_chords_no_simple = sorted(
        list(set(used_chords) - set(["N.C.", "Am", "C", "F", "G"])),
        key=chord_sort_key,
    )

    ###
    # Checks
    message = ""
    tab = "    "

    if diagrams != diagrams_sort:
        message += f"{tab}Warning: Chord diagrams should be sorted!\n"
        message += f"{tab}{tab}diagrams: {diagrams}\n"
        message += f"{tab}{tab}sorted:   {diagrams_sort}\n"

    if diagrams_sort != used_chords_uniq_sort and diagrams_sort != used_chords_no_simple:
        message += f"{tab}Warning: Used chords list does not match the diagrams!\n"
        message += f"{tab}{tab}diagrams:    {diagrams_sort}\n"
        message += f"{tab}{tab}used chords: {used_chords_uniq_sort}\n"

    return message


def chord_sort_key(ch):
    """
    >>> chord_sort_key("Abmaj7")
    ['A', -1, 0, 'maj7']
    >>> chord_sort_key('Gm')
    ['G', 0, 1, '']
    >>> chord_sort_key('Esharpsus4')
    ['E', 1, 0, 'sus4']
    >>> chord_sort_key('G7sus4')
    ['G', 0, 0, '7sus4']
    """
    # base note
    key = [ch[0]]
    i = 1

    # flat / natural / sharp
    if i < len(ch) and ch[i] == "b":
        key.append(-1)
        i += 1
    elif ch[i:].startswith("sharp"):
        key.append(1)
        i += 5
    else:
        key.append(0)


    # major / minor
    if i < len(ch) and ch[i] == "m" and not ch[i:].startswith("maj"):
        key.append(1)
        i += 1
    else:
        key.append(0)

    # the rest
    key.append(ch[i:])

    return key


if __name__ == "__main__":
    main()
