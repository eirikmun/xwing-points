from pathlib import Path
import json
import os
import sys


def buildPilotDatabase(path: Path):
    manifest_file = open(
        path / "data" / "manifest.json", mode="r", encoding="utf-8"
    )
    manifest = json.load(manifest_file)
    db = {}
    for faction_pilots in manifest["pilots"]:
        faction = faction_pilots["faction"]
        print(f"Parsing {faction} pilots")
        db[faction] = {}
        for ship_path in faction_pilots["ships"]:
            ship_file = open(path / ship_path, mode="r", encoding="utf-8")
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
    manifest_file = open(
        path / "data" / "manifest.json", mode="r", encoding="utf-8"
    )
    manifest = json.load(manifest_file)
    db = {}
    for upgrade_slot in manifest["upgrades"]:
        print(f"Parsing {upgrade_slot} upgrades")
        slot_file = open(path / upgrade_slot, mode="r", encoding="utf-8")
        upgrades = json.load(slot_file)
        for upgrade in upgrades:
            if (
                not upgrade.get("standardLoadoutOnly", False)
                and "cost" in upgrade
            ):
                print(f"Upgrade: {upgrade['name']}")
                db[upgrade["xws"]] = {
                    "name": upgrade["name"],
                    "cost": upgrade.get("cost", {}),
                    "limited": upgrade["limited"],
                    "standard": upgrade["standard"],
                    "wildspace": upgrade["wildspace"],
                    "epic": upgrade["epic"],
                    "restrictions": upgrade.get("restrictions", []),
                    "slots": upgrade["sides"][0]["slots"],
                }

    return db


def savePoints(pilots, upgrades, revision, revision_data):
    try:
        reivison_path = Path(os.getcwd(), "revisions", revision)
        os.makedirs(reivison_path)
    except FileExistsError:
        print(f"Revision {revision} allready exists")
        raise

    for faction in pilots:
        pointsfile = open(
            reivison_path / f"{faction}.json", mode="w", encoding="utf-8"
        )
        json.dump(pilots[faction], pointsfile, indent=4)
    pointsfile = open(
        reivison_path / "upgrades.json", mode="w", encoding="utf-8"
    )
    json.dump(upgrades, pointsfile, indent=4)

    revisionfile = open(
        reivison_path / "revision.json", mode="w", encoding="utf-8"
    )
    json.dump(revision_data, revisionfile, indent=4)


def main(revision):
    pilotdb = buildPilotDatabase(Path(os.getcwd(), "xwing-data2-legacy"))
    upgradedb = buildUpgradeDatabase(Path(os.getcwd(), "xwing-data2-legacy"))
    savePoints(
        pilotdb,
        upgradedb,
        revision,
        {
            "effective_date": "2024-03-26",
            "format": "March 2024 update",
            "author": "X2PO",
            "subject": "The X-Wing 2.0 Legacy regular points update",
            "files": {
                "rebelalliance": "X2PO/{revision}/rebelalliance.json",
                "galacticempire": "X2PO/{revision}/galacticempire.json",
                "scumandvillainy": "X2PO/{revision}/scumandvillainy.json",
                "resistance": "X2PO/{revision}/resistance.json",
                "firstorder": "X2PO/{revision}/firstorder.json",
                "galacticrepublic": "X2PO/{revision}/galacticrepublic.json",
                "separatistalliance": "X2PO/{revision}/separatistalliance.json",
                "upgrades": "X2PO/{revision}/upgrades.json",
            },
        },
    )


if __name__ == "__main__":
    print(__name__)
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Missing argument, usage: parsepoints.py <revision_name>")
