#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
REPO='PeterxVarga/ecosim-5y-decision-mvp'
RELEASE='ECOSIM_R162_INTEGRITY_REVIEW_RC_20261031.zip'
SOURCE='ECOSIM_R162_INTEGRITY_REVIEW_RC'
TAG='r162-20261031'
ZIP_SHA='731c5b823099421e099b748102fac8ae93a2b41f72dd196cafaca2cafb2d5908'

die() { printf 'HIBA: %s\n' "$*" >&2; exit 2; }
command -v git >/dev/null || die 'Git nincs telepitve (sudo dnf install git)'
command -v gh >/dev/null || die 'GitHub CLI (gh) hianyzik: sudo dnf install gh'
command -v python3 >/dev/null || die 'Python3 hianyzik'
command -v sha256sum >/dev/null || die 'sha256sum hianyzik'
command -v unzip >/dev/null || die 'unzip hianyzik (sudo dnf install unzip)'

printf '%s  %s\n' "$ZIP_SHA" "$RELEASE" | sha256sum -c - || die 'Az eredeti R162 ZIP nem egyezik'
unzip -tq "$RELEASE" || die 'Serult release ZIP'
[[ -d "$SOURCE" && ! -L "$SOURCE" ]] || die 'A forraskonyvtar hianyzik'
[[ -z "$(find "$SOURCE" -type l -print -quit)" ]] || die 'Szimbolikus link a forrasban'
(
  cd "$SOURCE"
  bash verify_release_r162.sh
) || die 'Az R162 forrasellenorzese nem sikerult'

if ! gh auth status >/dev/null 2>&1; then
  printf '\nGitHub-bejelentkezes szukseges (webes kodos folyamat).\n'
  gh auth login --web --git-protocol https || die 'Sikertelen GitHub bejelentkezes'
fi
CURRENT_LOGIN="$(gh api user --jq '.login')" || die 'Nem olvashato a GitHub felhasznalo'
[[ "$CURRENT_LOGIN" == 'PeterxVarga' ]] || die "Masik GitHub-fiok aktiv: $CURRENT_LOGIN (vart: PeterxVarga)"

if [[ ! -d .git ]]; then
  git init -b main
fi
[[ "$(git branch --show-current)" == 'main' ]] || die 'Nem main agat hasznalsz'

git add -- README.md RELEASE_NOTES.md publish_private.sh .gitignore "$SOURCE"
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  NAME="$(git config user.name || true)"
  EMAIL="$(git config user.email || true)"
  [[ -n "$NAME" ]] || NAME="$CURRENT_LOGIN"
  [[ -n "$EMAIL" ]] || EMAIL='117763198+PeterxVarga@users.noreply.github.com'
  git -c user.name="$NAME" -c user.email="$EMAIL" commit -m 'Import EcoSim R162 offline release candidate (verified source)'
fi
[[ -z "$(git status --porcelain)" ]] || die 'Helyi modositas van: nem publikalok bizonytalan fat'
LOCAL_SHA="$(git rev-parse HEAD)"

if gh repo view "$REPO" >/dev/null 2>&1; then
  PRIVACY="$(gh repo view "$REPO" --json isPrivate --jq '.isPrivate')"
  [[ "$PRIVACY" == 'true' ]] || die 'A letezo repository NEM privat; megszakitva'
  REMOTE_SHA="$(gh api "repos/$REPO/git/ref/heads/main" --jq '.object.sha' 2>/dev/null || true)"
  [[ "$REMOTE_SHA" == "$LOCAL_SHA" ]] || die 'A repo mar letezik es tartalma elter: nem irjuk felul'
  printf 'Privat repository es identikus main mar letezik.\n'
else
  printf '\nUj PRIVAT repository letrehozasa es forras feltoltese: %s\n' "$REPO"
  gh repo create "$REPO" --private --source=. --remote=origin --push || die 'GitHub repo feltoltes sikertelen'
fi

[[ "$(gh repo view "$REPO" --json isPrivate --jq '.isPrivate')" == 'true' ]] || die 'GitHub-adatvedelmi ellenorzes sikertelen'
[[ "$(gh api "repos/$REPO/git/ref/heads/main" --jq '.object.sha')" == "$LOCAL_SHA" ]] || die 'GitHub main commit nem egyezik'
if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  gh release view "$TAG" --repo "$REPO" --json assets --jq '.assets[].name' | grep -Fxq "$RELEASE" || die 'A release letezik, de a ZIP-melleklet hianyzik'
else
  gh release create "$TAG" "$RELEASE" --repo "$REPO" --target main --title 'R162 — Offline Decision MVP Release Candidate' --notes-file RELEASE_NOTES.md || die 'A repo fent van, de a GitHub Release feltoltese megakadt'
fi

printf '\nSIKER: PRIVAT repo + teljes forraskod + R162 Release ZIP\n'
printf 'Repo: https://github.com/%s\n' "$REPO"
printf 'Release: https://github.com/%s/releases/tag/%s\n' "$REPO" "$TAG"
printf 'Commit: %s\n' "$LOCAL_SHA"
printf 'Gaming action gate: STOP. Valos strategia-pontossag: UNKNOWN.\n'
