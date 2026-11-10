# Gartentierkompass

Statische Website für gartentierkompass.de – Tiere im Garten bestimmen.

Die fertigen Seiten liegen im Hauptordner und werden bei statichost.eu direkt ausgeliefert.
Im Ordner `_quelle` liegt der Generator (Python). Aufbau und Aufruf stehen in `_quelle/README.md`.
Neu bauen: `cd _quelle && GTK_OUT=.. python3 build.py && python3 -m tools.check`
