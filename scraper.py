import argparse
import json
import os
from collections import Counter
from itertools import product
from timeit import default_timer as timer

from anvil import Chunk, Region

parser = argparse.ArgumentParser()
parser.add_argument('--world', required=True, help='Name of the Minecraft world to scrape')
parser.add_argument('--out', default='dataset.json', help='File to output data to')
parser.add_argument('--spiral', action='store_true', help='Set flag to scrape regions in a spiral order')
args = parser.parse_args()


def spiral_step(t):
    x, y = t
    # Starts (0,0) -> (1,0) and continues anti-clockwise
    if x > y > -1 * x:
        y += 1  # Walk UP
    elif y >= x and y > -1 * x:
        x -= 1  # Walk LEFT
    elif x < y <= -1 * x:
        y -= 1  # Walk DOWN
    elif y <= x and y <= -1 * x:
        x += 1  # Walk RIGHT
    return x, y


if os.name == 'nt':
    minecraft_path = os.environ.get("APPDATA")
elif os.name == 'posix':
    minecraft_path = os.environ.get("HOME")
else:
    print(f'Unable to get Minecraft path from: {os.name}')
    raise OSError
world_folder = os.path.join(minecraft_path, '.minecraft/saves', args.world)

try:
    print(f"Loading existing output JSON: {args.out}")
    with open(args.out) as f:
        output_JSON = json.load(f)
        layers = {int(k): Counter(v) for k, v in output_JSON['layers'].items()}
        latest_chunk, latest_r = tuple(output_JSON['latest']['chunk']), output_JSON['latest']['region']
except FileNotFoundError:
    print(f"FileNotFoundError: Creating new output file: {args.out}")
    layers = {y: Counter() for y in range(-64, 320)}
    latest_chunk, latest_r = (0, 0), (0, 0)


def iterate_regions(_region, spiral_path=False):
    _x, _z = (0, 0) if _region is None else _region
    yield _x, _z
    while True:
        if spiral_path:
            _x, _z = spiral_step((_x, _z))
        else:
            _z += 1
        yield _x, _z


def chunk_eta(_chunk, _timing_list, _start_timer, _end_timer, _latest_chunk, _latest_region, _rx, _rz):
    chunk_elapsed = _end_timer - _start_timer
    _timing_list.append(chunk_elapsed)
    chunks_done = len(_timing_list)
    remaining_chunks = sum(1 for _chunk in product(range(32), range(32)) if _chunk > _latest_chunk)
    avg_time = sum(_timing_list) / chunks_done
    eta_sec1 = avg_time * remaining_chunks
    eta_min = int(eta_sec1 // 60)
    eta_sec2 = int(eta_sec1 % 60)
    if _chunk[1] == 31:
        print(
            f' | Scraped: {_chunk} in {chunk_elapsed:.4f}s | [REGION] ({_rx}, {_rz}) {(1024 - remaining_chunks) / 1024 * 100:.2f}% done, {eta_min}m {eta_sec2}s remains')
    else:
        print(f' | Scraped: {_chunk} in {chunk_elapsed:.4f}s')


print(f'Starting in r: {latest_r}, c: {latest_chunk}')
print(f"Spiral: {args.spiral}")
for region_x, region_y in iterate_regions(latest_r, args.spiral):  # Steps through regions
    print(f'[REGION] In: ({region_x}, {region_y})')
    region_start_timer = timer()
    try:
        region = Region.from_file(f'{world_folder}/region/r.{region_x}.{region_y}.mca')
        print(f'[REGION] Found: ({region_x}, {region_y})')
    except FileNotFoundError:
        print(f"[REGION] File r.{region_x}.{region_y}.mca not found, skipping.")
        continue
    chunk_time = []
    for working_chunk_coords in product(range(32), range(32)):  # Steps through chunks
        print(f"[CHUNK] {working_chunk_coords} processing...", end='', flush=True)
        chunk_start_timer = timer()
        try:
            if Region.chunk_location(region, *working_chunk_coords)[0] != 0 and working_chunk_coords > latest_chunk:
                current_chunk = Chunk.from_region(region, *working_chunk_coords)
            elif Region.chunk_location(region, *working_chunk_coords)[0] == 0:
                print(f" | {working_chunk_coords} is empty, skipping.")
                continue
            elif working_chunk_coords <= latest_chunk:  # this doesn't count chunk (0, 0) when the loop begins each time
                print(f" | {working_chunk_coords} is already processed, skipping.")
                continue
            else:
                print(f" | {working_chunk_coords} is unable to be processed, skipping.")
                continue
        except (IndexError, ValueError) as e:
            print(f" | Invalid {working_chunk_coords} ({type(e).__name__}: {e}), skipping.")
            continue

        for coords in product(range(16), range(-64, 320), range(16)):  # Steps through individual blocks
            x, y, z = coords
            block = current_chunk.get_block(*coords)
            layers[y][block.id] += 1
        latest_chunk = working_chunk_coords
        with open(args.out, 'w') as o:
            json.dump({'latest': {'region': [region_x, region_y], 'chunk': latest_chunk},
                       'layers': layers}, o, indent=2)
        chunk_end_timer = timer()
        chunk_eta(working_chunk_coords, chunk_time, chunk_start_timer, chunk_end_timer, latest_chunk, latest_r, region_x, region_y)
    region_end_timer = timer()
    print(f'[REGION] Scraped: ({region_x}, {region_y}) in {region_end_timer - region_start_timer:.4f}s')
    latest_chunk = (0, 0)
