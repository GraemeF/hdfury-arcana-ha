The title of this pull request becomes the commit subject on `main`. The merge
is a squash, so the title is the only line of your branch that `main` keeps,
and CI checks that it is a Conventional Commit. Get the verdict now rather
than after a failed check:

    scripts/conventional-subject.sh '<your title>'

If the change needs the device, say what you ran against a real Arcana and on
which firmware. CONTRIBUTING.md has the rest.
