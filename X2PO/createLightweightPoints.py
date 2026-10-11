from pathlib import Path
import json
import os
import sys


def resolve_data_paths(input_path: Path):
    if (input_path / "manifest.json").is_file():
        manifest_path = input_path / "manifest.json"
        repo_root = input_path.parent
    elif (input_path / "data" / "manifest.json").is_file():
        manifest_path = input_path / "data" / "manifest.json"
        repo_root = input_path
    else:
        raise FileNotFoundError(
            f"Could not find manifest.json in {input_path} or {input_path / 'data'}"
        )
    return manifest_path, repo_root


def buildPilotDatabase(path: Path):
    manifest_path, repo_root = resolve_data_paths(path)
    with open(manifest_path, mode="r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)
    db = {}
    for faction_pilots in manifest["pilots"]:
        faction = faction_pilots["faction"]
        print(f"Parsing {faction} pilots")
        db[faction] = {}
        for ship_path in faction_pilots["ships"]:
            with open(repo_root / ship_path, mode="r", encoding="utf-8") as ship_file:
                ship_pilots = json.load(ship_file)
            ship = ship_pilots["name"]
            db[faction][ship] = {}
            for pilot in ship_pilots["pilots"]:
                pilot_data = {
                    "name": pilot["name"],
                    "subtitle": pilot.get("caption", ""),
                    "limited": pilot["limited"],
                    "cost": pilot["cost"],
                    "slots": pilot.get("slots", []),
                    "keywords": pilot.get("keywords", []),
                    "standard": "Yes" if pilot["standard"] else "No",
                    "wildspace": "Yes" if pilot["wildspace"] else "No",
                    "epic": "Yes" if pilot["epic"] else "No",
                }
                # Conditionally add 'standardLoadout' if it exists
                if "standardLoadout" in pilot:
                    pilot_data["standardLoadout"] = pilot["standardLoadout"]

                db[faction][ship][pilot["xws"]] = pilot_data
    return db


def buildUpgradeDatabase(path: Path):
    manifest_path, repo_root = resolve_data_paths(path)
    with open(manifest_path, mode="r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)
    db = {}
    for upgrade_slot in manifest["upgrades"]:
        print(f"Parsing {upgrade_slot} upgrades")
        with open(repo_root / upgrade_slot, mode="r", encoding="utf-8") as slot_file:
            upgrades = json.load(slot_file)
        for upgrade in upgrades:
            if (
                not upgrade.get("standardLoadoutOnly", False)
                and "cost" in upgrade
            ):
                print(f"Upgrade: {upgrade['name']}")
                restrictions = upgrade.get("restrictions", [])

                db[upgrade["xws"]] = {
                    "name": upgrade["name"],
                    "cost": upgrade.get("cost", {}),
                    "limited": upgrade["limited"],
                    "standard": upgrade["standard"],
                    "wildspace": upgrade["wildspace"],
                    "epic": upgrade["epic"],
                    "restrictions": restrictions,
                    "slots": upgrade["sides"][0]["slots"],
                }

    return db


def savePoints(pilots, upgrades, revision, revision_data, output_dir: Path = None):
    if output_dir is None:
        revision_path = Path(__file__).resolve().parent / revision
    else:
        revision_path = output_dir / revision

    os.makedirs(revision_path, exist_ok=True)

    for faction in pilots:
        with open(revision_path / f"{faction}.json", mode="w", encoding="utf-8") as pointsfile:
            json.dump(pilots[faction], pointsfile, ensure_ascii=False, indent=4)
    with open(revision_path / "upgrades.json", mode="w", encoding="utf-8") as pointsfile:
        json.dump(upgrades, pointsfile, ensure_ascii=False, indent=4)

    with open(revision_path / "revision.json", mode="w", encoding="utf-8") as revisionfile:
        json.dump(revision_data, revisionfile, ensure_ascii=False, indent=4)


def main(revision, data_path=None):
    if data_path is None:
        candidates = [
            Path(os.getcwd(), "xwing-data2-legacy"),
            Path(__file__).resolve().parent.parent.parent / "xwing-data2-legacy",
            Path("p:/xwing-data2-legacy"),
            Path("p:/xwing-data2-legacy/data"),
            Path(os.getcwd()),
        ]
        for c in candidates:
            if (c / "manifest.json").is_file() or (c / "data" / "manifest.json").is_file():
                data_path = c
                break
        if data_path is None:
            raise FileNotFoundError("Could not find xwing-data2-legacy repository or data directory")
    else:
        data_path = Path(data_path)

    pilotdb = buildPilotDatabase(data_path)
    upgradedb = buildUpgradeDatabase(data_path)
    savePoints(
        pilotdb,
        upgradedb,
        revision,
        {
            "effective_date": "2026-09-26",
            "format": "September 2026 update",
            "author": "X2PO",
            "subject": "The X-Wing 2.0 Legacy regular points update",
            "files": {
                "rebelalliance": f"X2PO/{revision}/rebelalliance.json",
                "galacticempire": f"X2PO/{revision}/galacticempire.json",
                "scumandvillainy": f"X2PO/{revision}/scumandvillainy.json",
                "resistance": f"X2PO/{revision}/resistance.json",
                "firstorder": f"X2PO/{revision}/firstorder.json",
                "galacticrepublic": f"X2PO/{revision}/galacticrepublic.json",
                "separatistalliance": f"X2PO/{revision}/separatistalliance.json",
                "upgrades": f"X2PO/{revision}/upgrades.json",
            },
        }
    )


if __name__ == "__main__":
    print(__name__)
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Missing argument, usage: createLightweightPoints.py <revision_name> [data_path]")
