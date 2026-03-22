# HDFury Arcana HA Integration

Home Assistant custom integration for the HDFury Arcana, communicating over
RS-232 serial.

## Build Pipeline

This project uses [go-task](https://taskfile.dev/) for all build, test, lint,
and format operations. **Never invoke pytest, ruff, or pip directly.** Always
use the corresponding task.

### Available Tasks

| Command             | What it does                                      |
| ------------------- | ------------------------------------------------- |
| `task setup`        | Create `.venv/` and install all deps              |
| `task format`       | Auto-format Python code with ruff                 |
| `task format-check` | Check formatting without changing files            |
| `task lint`         | Run ruff linter                                   |
| `task unit-test`    | Run full test suite (runs format-check + lint first) |
| `task test`         | Full "safe to merge" gate                         |

### Dependency Chain

```
setup → format-check + lint → unit-test → test
```

Tasks cache based on source file hashes. If nothing changed, the task is
skipped. Use `task --force <name>` to bypass caching.

### First Time Setup

```bash
nix develop          # enter the dev shell (provides python, go-task, ruff, bd)
task setup           # create venv, install deps
task test            # run the full pipeline
```

## Project Structure

```
custom_components/hdfury_arcana/
├── __init__.py        # Integration setup/teardown (runtime_data pattern)
├── const.py           # DOMAIN constant
├── coordinator.py     # DataUpdateCoordinator (polls device every 5 min)
├── entity.py          # Base entity class (CoordinatorEntity)
├── manifest.json      # HA integration manifest
└── serial_client.py   # Async serial client (pyserial-asyncio-fast)

tests/                 # pytest tests (pytest-homeassistant-custom-component)
```

## Serial Protocol

- 19200 baud, 8N1, no handshake
- Commands: `#arcana get|set <param> [value]\r`
- Responses: single line terminated with `\r\n`
- All access serialised through `asyncio.Lock`
