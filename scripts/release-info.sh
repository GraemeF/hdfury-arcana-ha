#!/usr/bin/env bash
# Prints the release that the manifest's version describes, as key=value lines
# that a GitHub Actions step can append to $GITHUB_OUTPUT:
#
#   version=0.5.0-beta.1
#   tag=v0.5.0-beta.1
#   notes=RELEASE-NOTES/0.5.0-beta.1.md
#   prerelease=true
#
# A version with a suffix after a hyphen is a pre-release.
# Fails when the version has no release notes file.

set -euo pipefail

cd "$(dirname "$0")/.."

manifest=custom_components/hdfury_arcana/manifest.json
version=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["version"])' "$manifest")
notes="RELEASE-NOTES/$version.md"

if [[ ! -s "$notes" ]]; then
    echo "$manifest has version $version, but $notes is missing or empty." >&2
    echo "Add the release notes for $version in $notes." >&2
    exit 1
fi

if [[ "$version" == *-* ]]; then
    prerelease=true
else
    prerelease=false
fi

echo "version=$version"
echo "tag=v$version"
echo "notes=$notes"
echo "prerelease=$prerelease"
