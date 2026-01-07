def load_map(filename):
    map_data = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            row = [c for c in line.strip().split()]
            map_data.append(row)
    return map_data
