# Gartentierkompass

Statische Website für gartentierkompass.de – Tiere im Garten bestimmen.

Die fertigen Seiten liegen in `dist/` und werden bei statichost.eu direkt ausgeliefert (siehe `statichost.yml`, nur `dist/` ist öffentlich).
Im Ordner `_quelle` liegt der Generator (Python). Aufbau und Aufruf stehen in `_quelle/README.md`.
Neu bauen: `cd _quelle && python3 build.py && python3 -m tools.check`
