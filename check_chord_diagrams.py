from pathlib import Path
import re

import click
import click_pathlib


ignored_files = [
    "songs/marniva_sesternice__jiri_suchy.tex",
    "songs/under_the_bridge__red_hot_chilli_peppers.tex",
]


@click.command("Check that diagrams are listed for all used song chords.")
@click.option(
    "-i",
    "--song-dir",
    required=True,
    type=click_pathlib.Path(exists=True),
    help="input directory with songs",
)
@click.option(
    "-r",
    "--report_ignored",
    is_flag=True,
    help="report warnings also for files in the ignore list",
)
@click.option(
    "-p",
    "--print-tex-code",
    is_flag=True,
    help="print tex code with all used chords for songs with detected warnings",
)
def main(song_dir: Path, report_ignored: bool, print_tex_code: bool) -> None:
    num_warn_files = 0
    for song_filename in song_dir.glob("*.tex"):
        # Run chord parsing also for ignored files.
        song_file_str = song_filename.read_text()
        warn_message = check_file(song_file_str, print_tex_code)

        if warn_message and (
            report_ignored or str(song_filename) not in ignored_files
        ):
            num_warn_files += 1
            print(song_filename)
            print(warn_message)

    if num_warn_files == 0:
        print("All checks OK.")
    else:
        print(f"Warnings in {num_warn_files} song files.")


def check_file(song_file_str: str, print_tex_code: bool) -> str:
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

    # Between curly brackets in \ch{...}, take all alphanum+ characters from
    # the beginning, after an optional star. This is to exclude \rep, \beats
    # or other special instructions inside. Besides alphanum, also include:
    # - '.' to handle "N.C."
    # - '/' to handle slash chords
    # - '-' to handle e.g. (Am-G-F)
    used_chords_plus = re.findall(
        r"\\ch\{\*?([\w\./-]+)[^\}]*\}",
        tex_code,
        re.DOTALL | re.UNICODE,
    )
    used_chords = flatten([x.split('-') for x in used_chords_plus])

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
        message += f"{tab}Warning: Used chord list does not match the diagrams!\n"
        message += f"{tab}{tab}diagrams:    {diagrams_sort}\n"
        message += f"{tab}{tab}used chords: {used_chords_uniq_sort}\n"

    if print_tex_code and message:
        message += f"{tab}Tex code:\n"
        message += "\n".join(
            [f"{tab}{tab}\\ukechord{{{ch}}}" for ch in used_chords_uniq_sort]
        )
        message += "\n"

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


def flatten(t):
    return [item for sublist in t for item in sublist]


if __name__ == "__main__":
    main()
