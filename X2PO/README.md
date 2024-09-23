# X-Wing 2.0 Legacy project points

This is where The X2PO will publish their Legacy points in a tools friendly json format.
The cards are referenced by their xws value, collected from the https://github.com/SogeMoge/xwing-data2-legacy repository.

> Legacy uses separate repository and implements several changes like:

- **standardLoadout** field for pilots whih lists SL upgrades;
- Left Side Legal versions of SL cards
- Outrider 2023 reprint
- Legacy card images with legacy errata;
- **standard** + **wildspace** + **epic** gamemodes ("extended" renamed to "standard" and "hyperspace" renamed to "wildspace")

To generate new revision of points you can use `createLightweightPoints.py` python scipt, running it in from same direcory with xwing-data2-legacy repository.