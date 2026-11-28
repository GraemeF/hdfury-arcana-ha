# Releasing

A release is one pull request. Merging it to `main` publishes the release,
and no step follows by hand.

## The release pull request

The release pull request does two things:

1. It sets `version` in `custom_components/hdfury_arcana/manifest.json` to
   the new version.
2. It adds the release notes as `RELEASE-NOTES/<version>.md`. This file
   becomes the body of the GitHub release.

The test pipeline fails when the manifest's version has no notes file, so a
release pull request without notes cannot pass CI.

## Versions

Versions follow semantic versioning. A version with a suffix after a hyphen,
such as `0.5.0-beta.1`, is published as a pre-release. HACS offers a
pre-release only to users who choose to show beta versions for this
integration. A version without a suffix, such as `0.5.0`, is a full release,
and HACS offers it to everyone.

The tag is the version with a `v` in front, such as `v0.5.0`.

## What the Release workflow does

The Release workflow runs when a push to `main` changes the manifest. It runs
the same checks as Validate on the merged commit. Then it tags that commit
with the manifest's version and publishes the GitHub release with the notes
file.

The workflow skips publishing when the tag already exists, because a change
to the manifest that keeps the version is not a release.

If a run fails before it publishes, fix the cause and re-run the workflow
from the Actions tab. The workflow creates the tag and the release together,
so a failed run leaves nothing to clean up.
