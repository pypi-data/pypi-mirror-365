```markdown
# yanghao.portlink

> Expose your local port to the public internet with a single command.

```bash
pip install yanghao.portlink
portlink tcp 8000
```

---

## 🚀 Quick Start

1. **Install**  
   ```bash
   pip install yanghao.portlink
   ```

2. **Expose a local TCP service**  
   ```bash
   portlink tcp 8000
   ```
   Output:
   ```
   ✓ Tunnel created
   Public URL: tcp://abc123.portlink.dev:8000 -> localhost:8000
   ```

3. **Programmatic usage**  
   ```python
   from yanghao.portlink import Client

   async with Client(token="YOUR_TOKEN") as c:
       url = await c.expose(8000, protocol="http")
       print(url)
   ```

---

## ✨ Features

- **Zero-config** – one binary, one command  
- **TCP protocol** – simple and reliable  
- **Auto-reconnect** – survives network hiccups  
- **Async & sync APIs** – fits any codebase  
- **Cross-platform** – Linux, macOS, Windows  

---

## 📦 Installation

| Method | Command |
|--------|---------|
| PyPI   | `pip install yanghao.portlink` |
| Source | `git clone https://github.com/yahao333/portlink && pip install -e .` |

Requires **Python 3.8+**.

It is recommended to use a virtual environment (`.venv`) to avoid dependency conflicts.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🛠 Usage

### CLI

| Command | Description |
|---------|-------------|
| `portlink tcp 8000` | Expose local port 8000 |
| `portlink tcp 22`    | Expose local SSH |
| `portlink --config ~/.portlink.yml` | Use custom config |

### Python API (sync)

```python
from yanghao.portlink import Client

client = Client(token="YOUR_TOKEN")
url = client.expose(8000, protocol="tcp")
print(url)  # tcp://abc123.portlink.dev:8000
```

### Python API (async)

```python
import asyncio
from yanghao.portlink import AsyncClient

async def main():
    async with AsyncClient(token="YOUR_TOKEN") as c:
        url = await c.expose(8000, protocol="tcp")
        print(url)  # tcp://abc123.portlink.dev:8000

asyncio.run(main())
```

---

## ⚙️ Configuration

Create `~/.portlink.yml`:

```yaml
token: YOUR_TOKEN
server: tcp://tunnel.portlink.dev
region: auto
```

Environment variables are also supported:
```bash
export PORTLINK_TOKEN="YOUR_TOKEN"
```

---

## 🔐 Authentication

1. [Sign in](https://portlink.dev) → Settings → **API Tokens**  
2. Copy the token, export or save in config.

---

## 🤝 Contributing

1. Fork the repo  
2. `pip install -e ".[dev]"`  
3. `pytest` (≥ 90 % coverage required)  
4. Open a PR

---

## 📄 License

MIT © 2025 yahao333

---

## 💬 Help

- [Discussions](https://github.com/yahao333/portlink/discussions)  
- [Issues](https://github.com/yahao333/portlink/issues)
```