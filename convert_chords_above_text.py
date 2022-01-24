from pathlib import Path

import click
import click_pathlib


def flatten(t):
    return [item for sublist in t for item in sublist]


def gen_all_chords() -> list[str]:
    # Does not need to be perfect
    alpha = ["A", "B", "C", "D", "E", "F", "G"]
    roots = flatten([[a, a+"b", a+"#"] for a in alpha])
    triads = flatten([[r, r+"m", r+"dim", r+"aug"] for r in roots])
    suffixes = ["", "7", "maj7", "sus2", "sus4", "7sus4", "6", "5", "9"]
    return [t+s for t in triads for s in suffixes]

ALL_CHORDS = gen_all_chords()


@click.command("Generate tex pseudo code from lyrics with chords above in plain text")
@click.option(
    "-i",
    "--song-text",
    type=click_pathlib.Path(exists=True),
    help="Input text file with chords above lyrics format",
)
def main(song_text: Path) -> None:
    song_text_str = song_text.read_text()
    lines = song_text_str.split("\n") + [""]
    skip_line = False
    for line, next_line in zip(lines, lines[1:]):
        if skip_line:
            skip_line = False
            continue

        # Handle paragraph breaks (empty lines)
        if not line.split():
            if not next_line.split():
                # Doubled empty line, process only the last one
                continue
            print("\n\\bigskip\n")
            continue

        if is_chord_line(line=line):
            output_line = merge_lines(chord_line=line, lyrics_line=next_line)
            skip_line = True
        else:
            output_line = line

        print(postprocess(line=output_line))


def is_chord_line(line: str) -> bool:
    # Returns true is at least 50% of tokens on a line are chords.
    # This heuristic is in place so that the chord list does not have perfect.
    # (Note: Non-empty whitespace-separated tokens)
    tokens = line.split()
    if not tokens:
        return(False)

    chord_tokens = [t for t in tokens if t in ALL_CHORDS]
    return(len(chord_tokens) / len(tokens) > 0.5)


def merge_lines(chord_line: str, lyrics_line: str):
    # Inserts chords from the chord_line at the right position into
    # lyrics_line. Extra features:
    # - A chord cannot be at the end of a word
    # - A chord cannot be right after the first letter of a word
    result_line = ""
    cpos = 0
    lpos = 0

    while cpos < len(chord_line):
        if chord_line[cpos] == " ":
            cpos += 1
            continue

        # New token starts at cpos
        token_end = cpos
        while token_end < len(chord_line) and chord_line[token_end] != " ":
            token_end += 1

        # Feature: Check whether after the first word letter
        is_after_letter = len(lyrics_line) >= cpos and lyrics_line[cpos-1] != " "
        is_two_after_whitespace = cpos <= 1 or len(lyrics_line) <= cpos - 2 or lyrics_line[cpos - 2] == " "
        is_after_first_letter = is_after_letter and is_two_after_whitespace
        
        # This is a bit hacky but as long as it usually works it is fine
        if is_after_first_letter:
            insert_lpos = cpos-1
        else:
            insert_lpos = cpos

        result_line += lyrics_line[lpos : insert_lpos]
        if len(lyrics_line) <= insert_lpos or lyrics_line[insert_lpos] == " ":
            # Feature: Prevent placing a chord at the end of a word
            result_line += " "    
        result_line += "\\ch{" + chord_line[cpos : token_end] + "}"
        result_line += lyrics_line[insert_lpos : token_end]
        cpos = token_end
        lpos = min(token_end, len(lyrics_line))

    if lpos < len(lyrics_line):
        result_line += lyrics_line[lpos:]

    return(result_line)


def postprocess(line: str) -> str:
    # Strip, merge spaces.
    line = " ".join(line.split())
    line += " \\par"
    line = line.replace("#", "\#")
    return(line)


if __name__ == "__main__":
    main()
