# 🚀 git-shield

`git-shield` is a lightweight, secure command-line tool that **detects hard-coded secrets, passwords, API keys, and random-looking sensitive data in your Git staged files before you commit.**

👌 Prevent accidental leaks
📊 Generate user-friendly reports
💪 Automate via Git pre-commit hooks
📈 Combines Regex + Shannon Entropy detection for maximum protection

---

## ✨ Features

- 🔍 Scans staged files for:

  - Hardcoded passwords
  - API keys
  - AWS secret keys
  - Private keys
  - Random-looking secrets (using Shannon Entropy)

- 📊 Detailed report: file, line, match type, code context
- ⚡ Fast and minimal dependencies (`click`, `rich`)
- ⚙️ Configurable patterns via optional JSON file
- 🔐 Designed for security (runs 100% locally)

---

## 📦 Installation

Ensure you have **Python 3.7+** installed.

```bash
# Install via PyPI
pip install git-shield
```

Alternatively:

```bash
git clone https://github.com/yourusername/git-shield.git
cd git-shield
pip install .
```

---

## ⚡ Quick Start

Run inside your Git project:

```bash
git-shield
```

👌 No secrets:

```
👌 No secrets detected. Proceeding with commit.
```

❌ Secrets detected:

```
❌ Secrets detected in staged files:

[src/config.py:10] Hardcoded password
  password = "MySecret123"

[src/api.py:45] High-Entropy String
  token = "f98A9dkJLqWE9s7fN..."

💡 Remove secrets before committing.
```

---

## 🛡 Git Pre-commit Hook

To block secrets automatically before every commit:

```bash
echo '#!/bin/sh
git-shield
' > .git/hooks/pre-commit

chmod +x .git/hooks/pre-commit
```

Every `git commit` will now trigger `git-shield`.

---

## ⚙️ Detection Method

- **Regex Detection:** Predefined + optional user-defined patterns.
- **Entropy Detection:** Flags random-looking secrets using Shannon Entropy.

---

## 🔐 Security Focus

- 100% local — no network calls.
- Does not store or upload your code.
- MIT Licensed — Open Source.

---

## 📖 Configurable Patterns

Define custom regex patterns in `patterns.json` (optional):

```json
{
  "Database URL": "postgres://[A-Za-z0-9:_@/]+"
}
```

`git-shield` will load and combine this with built-in patterns.

---

## ❗ Exit Codes

| Exit Code | Meaning                           |
| --------- | --------------------------------- |
| 0         | No secrets found — commit allowed |
| 1         | Secrets detected — commit blocked |
| 2         | Environment/tool errors.          |

Pseudo-logic: — commit blocked |

---

---

## 🤝 Author

👤 **Vamil Porwal**
[GitHub](https://github.com/VamilP)

---

## 📝 License

MIT License — Free to use, modify, and distribute.

---

## ❤️ Support

If you like this project, ⭐ star the repo and share it!
