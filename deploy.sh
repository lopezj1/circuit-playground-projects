#!/usr/bin/env bash
# Copy a project's .py files to the Circuit Playground Bluefruit.
#
#   ./deploy.sh 01            # matches projects/01-*
#   ./deploy.sh 02-fruit-piano
#   ./deploy.sh launcher      # menu + every game and its helper files
#   ./deploy.sh 05 --clean    # also remove other projects' files from the board
#   ./deploy.sh list          # show what can be deployed
#
# shared/*.py (helpers every game imports) is copied every time, along with
# the project's .py and .bmp files. Without --clean nothing on the board is
# deleted. --clean only removes .py/.bmp files that come from this repo and
# aren't part of this deploy; lib/, boot_out.txt and settings.toml are never
# touched.
# Set CIRCUITPY to override the board path (default: /d, or /mnt/d on WSL).
set -euo pipefail

cd "$(dirname "$0")"

list_projects() {
    echo "  launcher   (menu with every game)"
    for d in projects/*/; do
        d=${d%/}
        echo "  ${d#projects/}"
    done
}

clean=no
target=
for arg in "$@"; do
    case "$arg" in
        --clean) clean=yes ;;
        *) target=$arg ;;
    esac
done

if [ -z "$target" ] || [ $# -gt 2 ]; then
    echo "usage: ./deploy.sh <project> [--clean]   (e.g. 01, 05-buddy, launcher)"
    echo "       ./deploy.sh list"
    list_projects
    exit 1
fi

if [ "$target" = "list" ]; then
    echo "Deployable:"
    list_projects
    exit 0
fi

if [ -z "${CIRCUITPY:-}" ]; then
    if [ -d /mnt/d ]; then CIRCUITPY=/mnt/d; else CIRCUITPY=/d; fi
fi

if [ ! -f "$CIRCUITPY/boot_out.txt" ]; then
    echo "Board not found at $CIRCUITPY (no boot_out.txt)."
    echo "Plug it in, press reset once, and try again."
    exit 1
fi

if [ "$target" = "launcher" ]; then
    src=launcher
else
    matches=(projects/"$target"*/)
    if [ ! -d "${matches[0]}" ]; then
        echo "No project matching '$target'. Deployable:"
        list_projects
        exit 1
    fi
    if [ ${#matches[@]} -gt 1 ]; then
        echo "'$target' matches more than one project:"
        printf '  %s\n' "${matches[@]}"
        exit 1
    fi
    src=${matches[0]%/}
fi

if [ ! -f "$src/code.py" ]; then
    echo "$src has no code.py"
    exit 1
fi

shopt -s nullglob
files=(shared/*.py "$src"/*.py "$src"/*.bmp)
if [ "$src" = "launcher" ]; then
    # Every game plus its helper files (like a private halloween_songs.py).
    files+=(projects/*/*.py projects/*/*.bmp)
fi

# code.py goes last: the board restarts as soon as it changes, so every
# module it imports should already be there. *_example.py files are
# templates for the repo, not for the board.
for f in "${files[@]}"; do
    case "$(basename "$f")" in
        code.py | *_example.py) continue ;;
    esac
    cp "$f" "$CIRCUITPY/"
    echo "copied $(basename "$f")"
done

if [ "$clean" = yes ]; then
    # Remove files this repo put on the board for other projects. Only names
    # that exist in the repo are candidates, so nothing else is touched.
    keep=" code.py "
    for f in "${files[@]}"; do keep+="$(basename "$f") "; done
    for f in shared/*.py launcher/*.py projects/*/*.py projects/*/*.bmp; do
        name=$(basename "$f")
        case "$name" in *_example.py) continue ;; esac
        case "$keep" in *" $name "*) continue ;; esac
        if [ -f "$CIRCUITPY/$name" ]; then
            rm "$CIRCUITPY/$name"
            echo "removed $name"
            keep+="$name "
        fi
    done
fi

cp "$src/code.py" "$CIRCUITPY/"
echo "copied code.py"
sync
echo "Deployed $src. The board restarts on its own."
