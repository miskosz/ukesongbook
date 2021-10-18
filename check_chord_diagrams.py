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
    contents_preprocessed = song_file_str.replace("\\#", "sharp")


    # Everything between curly brackets in \ukechord{...} up until "_"
    diagrams = re.findall(
        r"\n\\ukechord\{([^\}_]+)[^\}]*\}",
        contents_preprocessed,
        re.DOTALL | re.UNICODE,
    )
    # Remove consecutive duplicates
    diagrams = [
        x for i, x in enumerate(diagrams)
        if i == len(diagrams) - 1 or x != diagrams[i + 1]
    ]
    diagrams_sort = sorted(diagrams)

    # Between curly brackets in \ch{...}, take all alphanum characters from
    # the beginning, after an optional star. This is to exclude \rep, \beats
    # or other special instructions inside. 
    used_chords = re.findall(
        r"\\ch\{\*?([\w\./]+)[^\}]*\}",
        contents_preprocessed,
        re.DOTALL | re.UNICODE,
    )
    # Sort and make unique. Remove "N.C."
    used_chords_uniq_sort = sorted(list(set(used_chords) - set(["N.C."])))
    used_chords_no_simple = sorted(list(set(used_chords) - set(["N.C.", "Am", "C", "F", "G"])))

    ###
    # Checks
    message = ""
    tab = "    "

    if diagrams != sorted(diagrams):
        message += f"{tab}Warning: Chord diagrams should be sorted!\n"
        message += f"{tab}{tab}diagrams: {diagrams}\n"
        message += f"{tab}{tab}sorted: {diagrams_sort}\n"

    if diagrams_sort != used_chords_uniq_sort and diagrams_sort != used_chords_no_simple:
        message += f"{tab}Warning: Used chords list does not match the diagrams!\n"
        message += f"{tab}{tab}diagrams: {diagrams_sort}\n"
        message += f"{tab}{tab}used chords: {used_chords_uniq_sort}\n"

    return message


if __name__ == "__main__":
    main()
