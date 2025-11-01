
#!/usr/bin/env bash
# Configure labels and create starter issues using GitHub CLI (gh).
set -e
echo "Creating labels..."
gh label create bug -c "#d73a4a" -d "Something isn't working" || true
gh label create enhancement -c "#a2eeef" -d "New feature or request" || true
gh label create documentation -c "#0075ca" -d "Improvements or additions to documentation" || true

echo "Creating roadmap issues..."
gh issue create -t "v1.1.0: Vision ONNX tuning & UI thresholds" -b "Specialized models + UI sliders" -l enhancement || true
gh issue create -t "v1.1.0: Long-term memory (vector DB)" -b "Light local vector store" -l enhancement || true
gh issue create -t "v1.1.0: SLAM 2D lightweight" -b "hector/karto with live map" -l enhancement || true
echo "Done."
