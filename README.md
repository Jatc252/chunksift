# chunksift, a Minecraft Data Visualisation Tool
> Forked from [0xTiger/blockheights](https://github.com/0xTiger/blockheights)

This script scrapes block distribution data from Minecraft (Java Edition) worlds by walking through each region and chunk in the Anvil file format.
It builds a JSON dataset structured by Y-level and block ID, useful for visualizing world generation patterns.

## Info
### Dataset
There is an example dataset at `dataset.json` that I generated which was made from a simple Minecraft world. The dataset was generated on `1.21.5 ` (March 2025) and contains over 1.89 billion blocks.
### Scraper
The region and chunk parsing is handled by [0xTiger’s fork](https://github.com/0xTiger/anvil-parser2) of the [anvil-parser](https://github.com/matcool/anvil-parser) library, which this script depends on.
### Visualisers
The original `oreheight_viz.py` and `blockheight_viz.py` scripts are still included here. Right now, both are deprecated and may not work as intended. I’m planning to fix and update them once the main scraper is fully polished.
### Arguments
- `--world WORLD` Name of the Minecraft world to scrape (must be located where the Microsoft launcher stores worlds)
- `--out OUT` File to output data to
- `--spiral` Set flag to scrape regions in a spiral order

## How to Scrape
### I want a new world
1. Create a Minecraft (Java Edition) world. You can use either the Microsoft launcher or a third party launcher such as [Prism Launcher](https://github.com/PrismLauncher/PrismLauncher).
2. Use a chunk generator like [Chunky](https://github.com/pop4959/Chunky) or explore the world to generate the chunks to scrape.
3. Close and save the world.
### I have an existing world
1. Close and save the world.
2. Ensure world is in the Microsoft launcher's default saves folder on your computer. I believe it's possible to scrape on worlds from a server, provided the region files are available at `.minecraft/saves/WORLD/region`.
3. If using a third party launcher, copy the world folder into `%appdata%/.minecraft/saves` or your OS's respective folder.
### For all worlds
4. Run `scraper.py` with your choice of arguments. Some example include:
   1. `scraper.py --world orescrape`
   2. `scraper.py --world orescrape --out data.json`
   3. `scraper.py --world orescrape --spiral`
   4. `scraper.py --world orescrape -out data.json --spiral`
5. Leave running until complete, or cancel at any time with CTRL+C.

## How to Analyse
### I want to see which Y level is most common for X ore
Simply run `analyse.py` and it will provide an analysis for you. `analyse.py` will provide Y level breakdown to the console, as well as providing a `ore_report.csv` that can be opened for an easily shareable analysis.
### I have my own JSON parser
Great! Good luck.
### I want a CSV file
Currently the scraper only outputs to JSON, but I have plans to create a full CSV converter in the future, rather than just the small CSV file that is created from `analyse.py`.
