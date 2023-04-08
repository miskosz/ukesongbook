from collections import Counter
from pathlib import Path
from pprint import pprint
import re

import click
import click_pathlib


@click.command("Check that diagrams are listed for all used song chords.")
@click.option(
    "-i",
    "--song-dir",
    default="songs",
    type=click_pathlib.Path(exists=True),
    help="Input directory with songs. Default: 'songs'",
)
def main(song_dir: Path) -> None:
    all_counter = Counter()
    song_counter = Counter()
    for song_filename in song_dir.glob("*.tex"):
        # if "bosorka" not in song_filename.name:
        #     continue
        song_file_str = song_filename.read_text()
        all, unique = _process_file(song_file_str)
        all_counter.update(all)
        song_counter.update(unique)

    print("Total chord counts (top 30):")
    _print_table(counter=all_counter)

    print()
    print("Number of songs using a chord (top 30):")
    _print_table(counter=song_counter)


def _print_table(counter: Counter) -> None:
    print("-" * 28)
    for i, (chord, count) in enumerate(counter.most_common(30)):
        print(f"  {i+1:3}. {chord:>14}: {count:4}")
        if (i+1) % 5 == 0:
            print("-" * 28)



def _process_file(song_file_str: str) -> tuple[Counter, Counter]:
    """
    Returns a tuple of two counters:
    - first counter counts all chords in the song
    - second counter counts only unique chords in the song
    """
    chord_list = _extract_chord_list(song_file_str=song_file_str)
    return Counter(chord_list), Counter(set(chord_list))


def _extract_chord_list(song_file_str: str) -> None:
    inside_ch_list = re.findall(
        r"\\ch\{([^\}]+)\}",
        song_file_str,
        re.DOTALL | re.UNICODE,
    )

    used_chords = _flatten(
        _extract_chord_names(inside_ch=ch)
        for ch in inside_ch_list
    )

    return used_chords


def _extract_chord_names(inside_ch: str) -> list[str]:
    """
    Extract the chord name. Handle special cases:
    - C\rep2
    - C\beat, C\beats2
    - \early C
    - N.C.
    - A/C
    - Am-G-F
    - C - single strum
    """
    # Replace \# by #
    inside_ch_1 = inside_ch.replace(r"\#", "#")

    # Remove all slash commands and potential trailing numbers
    inside_ch_2 = re.sub(r"\\[a-z]+\d*", "", inside_ch_1).strip()

    # Split by dash and trim
    chords_1 = [x.strip() for x in inside_ch_2.split("-")]

    # Remove "single strum"
    chords_2 = [ch for ch in chords_1 if ch != "single strum"]

    # Sanity check
    if not chords_2:
        raise RuntimeError(f"Could not parse '{inside_ch}'")

    # H4CK
    alpha = ["A", "B", "C", "D", "E", "F", "G"]
    roots = _flatten([[a+"b", a+"#", a] for a in alpha])
    for root in roots:
        chords_2 = [ch.removeprefix(root) for ch in chords_2]

    return chords_2


def _flatten(t):
    return [item for sublist in t for item in sublist]


if __name__ == "__main__":
    main()
