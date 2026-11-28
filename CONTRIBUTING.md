# Contributing to HDFury Arcana for Home Assistant

Thanks for looking. [README.md](README.md) says what the integration does, and
this guide says how to work on it.

## Reporting a bug, or proposing a change

Open a [GitHub issue](https://github.com/GraemeF/hdfury-arcana-ha/issues).
Give the integration's version, the Home Assistant version, the Arcana's
firmware version, and how the Arcana is connected.

A security bug is the exception. Report it as [SECURITY.md](SECURITY.md) says,
because an issue publishes the flaw before there is a fix.

## Getting a toolchain

The flake supplies Python, go-task and ruff:

```console
$ nix develop
$ task setup
```

`task setup` creates `.venv` and installs the dependencies into it. With
[direnv](https://direnv.net) installed, `direnv allow` enters the same shell
on every `cd` into the tree.

## Tests

```console
$ task test
```

`task test` is the gate. It checks formatting and lint, runs the tests, and
checks that the manifest's version has release notes. CI runs the same task,
so a pull request that passes it here passes the same checks in CI. Run
`task format` to fix formatting. Run tasks through `task` rather than calling
pytest or ruff yourself, because each task caches its result against its
source files.

The tests use
[pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
and never touch a real device. Shared fixtures live in `tests/conftest.py`.

**A change that needs the device needs someone who has one.** Say in the pull
request what you ran against a real Arcana, and on which firmware.

## Where things are

- `serial_client.py` speaks the Arcana's serial protocol.
- `coordinator.py` polls the device and holds what it said.
- One module per platform, such as `sensor.py` or `switch.py`, turns that into
  entities.
- `strings.json` holds the user-facing text. `task test` generates
  `translations/en.json` from it, so edit `strings.json` only.

[CLAUDE.md](CLAUDE.md) notes the protocol's quirks and the architecture's
rules, such as entities writing through the coordinator rather than the
client.

## Opening a pull request

Everything reaches `main` through a pull request, squash-merged.

**The title becomes the commit subject.** It is the only line of your branch
that `main` keeps, and CI refuses a title that is not a
[Conventional Commit](https://www.conventionalcommits.org):

    type(scope): description

- **type** is one of `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
  `refactor`, `revert`, `style` or `test`. A `!` before the colon marks a
  breaking change.
- **scope** is optional, in lower case, such as `sensor` or `config_flow`.
- **description** is in the imperative and has no full stop. It finishes the
  sentence "If applied, this commit will …".
- The whole title is at most **72 characters**.

Get the verdict CI will give before you open the pull request:

```console
$ scripts/conventional-subject.sh 'fix(sensor): read an unanswered parameter as unknown'
```

**The body becomes the commit body.** Say what changed and why, because the
diff already shows how.

## Licence

The integration is [Apache 2.0](LICENSE). Under section 5 of that licence, a
contribution you submit is under the same terms unless you say otherwise.
