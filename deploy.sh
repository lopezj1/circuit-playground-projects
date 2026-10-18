#!/usr/bin/env bash
# Copy a project's .py files to the Circuit Playground Bluefruit.
#
#   ./deploy.sh 01            # matches projects/01-*
#   ./deploy.sh 02-fruit-piano
#   ./deploy.sh launcher      # menu + every projects/*/game_*.py
#
# shared/*.py (helpers every game imports) is copied every time.
# Only code.py and project .py modules are written. Nothing on the board is
# ever deleted (lib/, boot_out.txt, settings.toml stay untouched).
# Set CIRCUITPY to override the board path (default: /d, or /mnt/d on WSL).
set -euo pipefail

cd "$(dirname "$0")"

if [ $# -ne 1 ]; then
    echo "usage: ./deploy.sh <project>   (e.g. 01, 02-fruit-piano, launcher)"
    echo "projects:"
    ls -1 projects
    exit 1
fi

if [ -z "${CIRCUITPY:-}" ]; then
    if [ -d /mnt/d ]; then CIRCUITPY=/mnt/d; else CIRCUITPY=/d; fi
fi

if [ ! -f "$CIRCUITPY/boot_out.txt" ]; then
    echo "Board not found at $CIRCUITPY (no boot_out.txt)."
    echo "Plug it in, press reset once, and try again."
    exit 1
fi

if [ "$1" = "launcher" ]; then
    src=launcher
else
    matches=(projects/"$1"*/)
    if [ ! -d "${matches[0]}" ]; then
        echo "No project matching '$1'. Projects:"
        ls -1 projects
        exit 1
    fi
    if [ ${#matches[@]} -gt 1 ]; then
        echo "'$1' matches more than one project:"
        printf '  %s\n' "${matches[@]}"
        exit 1
    fi
    src=${matches[0]%/}
fi

if [ ! -f "$src/code.py" ]; then
    echo "$src has no code.py"
    exit 1
fi

files=(shared/*.py "$src"/*.py)
if [ "$src" = "launcher" ]; then
    files+=(projects/*/game_*.py)
fi

# code.py goes last: the board restarts as soon as it changes, so every
# module it imports should already be there.
for f in "${files[@]}"; do
    [ "$(basename "$f")" = "code.py" ] && continue
    cp "$f" "$CIRCUITPY/"
    echo "copied $(basename "$f")"
done
cp "$src/code.py" "$CIRCUITPY/"
echo "copied code.py"
sync
echo "Deployed $src. The board restarts on its own."
