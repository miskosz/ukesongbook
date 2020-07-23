from pathlib import Path
import re

import click
import click_pathlib


@click.command("Generate an import file with a list of songs from a directory.")
@click.option(
    "-i",
    "--song-dir",
    required=True,
    type=click_pathlib.Path(exists=True),
    help="input directory with songs",
)
def main(song_dir: Path) -> None:
    """
    Writes a .tex file with a list of inputs. The file name is the song
    directory name concatenated with '.autogenerated.tex'.
    Sorts the inputs by a key constructed from the song title and artist.
    """
    key_and_file_pairs = []
    for song_file in song_dir.glob("*.tex"):
        match = re.match(
            r".*\\SongTitle\{(?P<title>[^\}]+)\}\{(?P<artist>[^\}]+)\}",
            song_file.read_text(),
            re.DOTALL | re.UNICODE,
        )
        if not match:
            raise ValueError(f"{song_file} does not seem to be a song file")
        key = match["title"] + " - " + match["artist"]
        key_and_file_pairs.append((key, song_file))

    output_file = song_dir.with_suffix(".autogenerated.tex")
    with output_file.open("w") as f:
        f.write(f"% THIS FILE IS AUTOGENERATED.\n")
        f.write(f"% DO NOT EDIT!\n")
        for _, song_file in sorted(key_and_file_pairs):
            f.write(f"\\input{{{song_file}}}\n")


if __name__ == "__main__":
    main()
