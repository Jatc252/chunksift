import json
import csv
from collections import defaultdict

# Load data from dataset.json
with open('out.json', 'r') as file:
    data = json.load(file)

# Dictionary to store ore occurrences by layer
ore_data = defaultdict(lambda: defaultdict(int))
total_blocks = 0
total_ores = 0

# Process the data
for layer, blocks in data["layers"].items():
    for block_name, count in blocks.items():
        total_blocks += count  # Sum all blocks
        if "_ore" in block_name:
            ore_data[block_name][int(layer)] = count
            total_ores += count

# Analyze and print the most common layer for each ore
csv_rows = []
for ore, layers in ore_data.items():
    sorted_layers = sorted(layers.items(), key=lambda x: x[1], reverse=True)

    most_common_layer = sorted_layers[0] if len(sorted_layers) > 0 else ("N/A", 0)
    second_common_layer = sorted_layers[1] if len(sorted_layers) > 1 else ("N/A", 0)
    third_common_layer = sorted_layers[2] if len(sorted_layers) > 2 else ("N/A", 0)

    total_occurrences = sum(layers.values())
    csv_rows.append([
        ore,
        most_common_layer[0], most_common_layer[1],
        second_common_layer[0], second_common_layer[1],
        third_common_layer[0], third_common_layer[1],
        total_occurrences
    ])
    print(f"{ore}:")
    print(f"  1st common at Y: {most_common_layer[0]} with {most_common_layer[1]} blocks.")
    print(f"  2nd common at Y: {second_common_layer[0]} with {second_common_layer[1]} blocks.")
    print(f"  3rd common at Y: {third_common_layer[0]} with {third_common_layer[1]} blocks.")
    total_occurrences = sum(layers.values())
    print(f"  Total occurrences analysed: {total_occurrences}\n")

# Write to CSV
with open('ore_report.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Ore Name",
        "Most Common Y", "Count",
        "Second Most Common Y", "Count",
        "Third Most Common Y", "Count",
        "Total Occurrences"
    ])
    writer.writerows(csv_rows)


print(f"Total number of blocks in the dataset: {total_blocks:,}")
print(f"Total number of ores in the dataset: {total_ores:,}")
ore_percent = (total_ores/total_blocks)*100
print(f"Percent of blocks that are ores: {ore_percent:.6f}%")