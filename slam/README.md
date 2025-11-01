# SLAM 2D — Squelette (v1.1.0)
Objectif: mettre en place l'affichage d'une carte 2D simple (mock) et la tuyauterie API/UI
sans dépendances lourdes pour démarrer. Étapes:
1) Générer une "occupancy grid" synthétique (PNG) à partir du LiDAR minimal (ou mock).
2) Servir /api/slam/map -> retourne le PNG.
3) UI: ajouter un <img> qui refresh toutes les 2-3s.
