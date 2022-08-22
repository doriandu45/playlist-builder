# PlaylistBuilder

Builds entire `.m3u8` playlists based on user-defined regexes and individual include and exclude lists

## How it works

Each playlist have its `.preset` file in the `presets` folder (examples included) that contains:
- One or more root path to explore
- Rules for including or excluding files based on their names (in python `re` regex form)

Additionaly, you can put `[preset name].include` and `[preset name].exclude` files in the folder that contains the music to force the script to include or exclude specific files

The rules are applied in this for each file order:
1. If the file is in the local `.include` file in its folder, we include it no matter what
2. If the file is in the local `.exclude` file in its folder, we exclude it no matter what
3. If the file match a global exclude regex, we exclude it
4. If the file match a global include regex (without being excluded before), we include it
5. If nothing matched, we don't include it

## Usage

Simply run the pyhton script `build.py` inside its folder. It doesn't use fancy libraries (just `os` and `re`) so nothing more is needed.

## Examples

Each example described here has its own example file in the `presets` folder

### Example 1

This example includes all mp3 and flac files found in two different folders. Note that absolute path works, but relative path are better if you want to export the playlist somewhere else (on your phone for example)

Since the preset use regexes, we can put `.mp3$` to indicate "files that **ends** with '.mp3'" and not just "files that **contains** '.mp3'", however this is not mandatory

### Example 2

This example include all `.flac` files that don't contain "Instrumental" or "instrumental" in the file name

Since, again, we use regexes, we can use the regex `[In]strumental` to match both cases, but we can also simply match "Instrumental" and "instrumental" separarely

### Example 3

We only set the root folder, but no regexes. By default, nothing will be matched but we can add files by using the `.include` files inside each folder. It's like making small playlists inside each folder, and merging them together (with the right path structure)

### Example 4

Merge Example 2 and 3 together. We could use the `NOWRITE` instruction to only have the result (`Example 4.m3u8`) but not `Example 2.m3u8` for example

## Commands available inside `.preset` files

`ROOT [path]`: add a root path to recursively search
`INCLUDE [regex]`: include all filenames that match this regex
`EXCLUDE [regex]`: exclude all filenames that match this regex
`IMPORT [preset name]`: insert a "sub-playlist" at the end of the current playlist. You can have multiple stacks of dependencies, but no loops
`NOWRITE`: do not write a m3u8 playlist at the end, but keep the result in memory. Useful for creating temporary "sub-playlists" that will be merged (and so written) elsewhere.

A preset file must contain at least one `ROOT` command (otherwise nothing will be scanned) or an `IMPORT` command. Other commands are not mandatory, and can be used multiple times to use multiple regexes.

Furthermore, you can put comments by beginning a line with `#`