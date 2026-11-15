#!/usr/bin/env bash
# Publica de forma segura el árbol íntegro de HALCONES ESTELARES GB 0.14.
# No borra ficheros ajenos ni hace push forzado. Requiere git y autorización GitHub en este ordenador.
set -euo pipefail
REPO="https://github.com/OnRail76/Halcones-Estelares-GB.git"
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
command -v git >/dev/null || { echo "ERROR: falta git" >&2; exit 1; }
[[ -f "$SOURCE/rom/Halcones-Estelares-GB-0.14.gb" ]] || { echo "ROM 0.14 no encontrada" >&2; exit 1; }
EXPECTED="d47bc5f3150d8de58d0737718badc62ba37b7dc0ada7c6b8205209ad2e12f2f7"
ACTUAL="$(sha256sum "$SOURCE/rom/Halcones-Estelares-GB-0.14.gb" | awk '{print $1}')"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo "ERROR: La ROM no coincide con 0.14" >&2; exit 1; }
TMP="$(mktemp -d)"
trap 'rm -rf -- "$TMP"' EXIT
printf '\nClonando %s ...\n' "$REPO"
git clone --branch main --single-branch "$REPO" "$TMP/repo"
# Copiamos solamente los archivos de este paquete: no se borran archivos preexistentes.
cp -a "$SOURCE"/. "$TMP/repo"/
git -C "$TMP/repo" add -A
if git -C "$TMP/repo" diff --cached --quiet; then
  echo "No hay cambios pendientes: el repositorio ya coincide con el paquete."
  exit 0
fi
if ! git -C "$TMP/repo" diff --cached --check; then
  echo "Advertencia: git encontró espacios en blanco a revisar." >&2
  exit 1
fi
if [[ -z "$(git -C "$TMP/repo" config user.name || true)" ]]; then
 git -C "$TMP/repo" config user.name "Tony C. Ware"
fi
if [[ -z "$(git -C "$TMP/repo" config user.email || true)" ]]; then
 git -C "$TMP/repo" config user.email "103560081+OnRail76@users.noreply.github.com"
fi
printf '\nArchivos preparados:\n'
git -C "$TMP/repo" diff --cached --stat
printf '\nPublicando como versión 0.14...\n'
git -C "$TMP/repo" commit -m "Publish Halcones Estelares Game Boy 0.14 with sources and documentation"
git -C "$TMP/repo" push origin main
printf '\nPUBLICACIÓN COMPLETA: https://github.com/OnRail76/Halcones-Estelares-GB\n'
