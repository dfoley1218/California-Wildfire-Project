from pathlib import Path
import json

# JSON files must be concatenated into a single file for pgSTAC to ingest.
def build_items_ndjson(catalog_dir="data/stac_catalog", out_path="data/stac_catalog/items.ndjson"):
    item_files = list(Path(catalog_dir).glob("fires-*/fires-*.json"))
    with open(out_path, "w") as out:
        for item_file in item_files:
            item = json.loads(item_file.read_text())
            out.write((json.dumps(item)) + "\n")
    print(len(item_files))

if __name__ == "__main__":
    build_items_ndjson()


