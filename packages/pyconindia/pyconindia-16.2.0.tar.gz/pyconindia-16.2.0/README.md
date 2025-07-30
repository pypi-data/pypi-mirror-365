# PyCon India

[![PyPI](https://img.shields.io/pypi/v/pyconindia?style=for-the-badge)](https://pypi.org/project/pyconindia/) ![PyPI - Downloads](https://img.shields.io/pypi/dw/pyconindia?style=for-the-badge) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconindia?style=for-the-badge)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  ![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/anistark/pyconindia)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/anistark/pyconindia)

[![Join PyCon India on Zulip](https://img.shields.io/badge/Join-Zulip-blue)](https://pyconindia.zulipchat.com/#narrow/stream/282100-2021.2Fpyconindia-team) [![Follow on Twitter](https://img.shields.io/twitter/follow/pyconindia?style=social&logo=twitter)](https://twitter.com/intent/follow?screen_name=pyconindia)

PyCon India is the largest gathering of Pythonistas in India for the Python programming language. The 13th edition of PyCon India will be taking place online from 17th September to 20th September 2021. With this unique scenario at hand, we plan to make this year's conference bigger, better, and more accessible to Pythonistas all across the world who can watch, participate and share their views right from the comfort of their homes.

## Installation

The `pyconindia` package works both as a **Python library** and a **command-line tool**.

### Install from PyPI (Recommended)

```bash
pip install pyconindia
```

### Install Globally (System-wide)

For system-wide installation that makes the CLI available to all users:

```bash
# Using pip (recommended)
pip install --user pyconindia

# Or install system-wide (requires admin/sudo)
sudo pip install pyconindia

# Using pipx (best practice for CLI tools)
pipx install pyconindia
```

**Note**: We recommend using `pipx` for CLI tools as it installs them in isolated environments while making them globally available.

### Install pipx (if not already installed)

```bash
# On macOS
brew install pipx

# On Ubuntu/Debian
sudo apt install pipx

# On other systems
python -m pip install --user pipx
python -m pipx ensurepath
```

## Usage

### As a Python Library

```python
>>> import pyconindia
>>> pyconindia.year
2025
>>> pyconindia.location
'Nimhans, Bengaluru, India'
>>> pyconindia.cfp
'Submit your proposal: https://cfp.in.pycon.org/2025/cfp'

# Using the Conference class
>>> from pyconindia.conference import Conference
>>> conf = Conference()
>>> conf.year()
2025
>>> conf.location(2024)
'Anywhere on Earth'
```

### As a Command Line Tool

After installation, you can use the CLI commands globally:

#### Basic Usage

```bash
# Show basic conference information
pyconindia

# Or use the shorter alias (not too short I guess 😅)
inpycon
```

Output:
```
🐍 Welcome to PyCon India CLI!
📅 Year: 2025
📍 Location: Nimhans, Bengaluru, India
📝 CFP: Submit your proposal: https://cfp.in.pycon.org/2025/cfp

Use --help to see all available commands.
```

#### Available Commands

```bash
# Get detailed conference information
pyconindia info
pyconindia info --year 2024        # For specific year
pyconindia info -y 2024            # Short form

# Get conference location
pyconindia location
pyconindia location --year 2024

# Get Call for Proposals information
pyconindia cfp
pyconindia cfp --year 2024

# Get current year
pyconindia year

# Show version
pyconindia version

# Show help
pyconindia --help
```

#### JSON Output

All commands support JSON output for integration with other tools:

```bash
# JSON output
pyconindia --json
pyconindia info --json
pyconindia location --json --year 2024
```

Example JSON output:
```json
{
  "year": 2025,
  "location": "Nimhans, Bengaluru, India",
  "cfp": "Submit your proposal: https://cfp.in.pycon.org/2025/cfp",
  "version": "16.0.0"
}
```

#### Enhanced Commands

```bash
# Show PyCon India history
pyconindia history
pyconindia history --start-year 2020 --end-year 2025

# Open PyCon India website
pyconindia website
pyconindia website --browser        # Opens in default browser
```

#### Command Aliases

For convenience, you can use either command name:

```bash
pyconindia info    # Full name
pycon info         # Short alias
```

## Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/anistark/pyconindia.git
cd pyconindia

# Install in development mode
pip install -e .

# Now you can use the CLI
pyconindia --help
```

### Testing

```bash
python test.py
```

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **Website**: [https://in.pycon.org](https://in.pycon.org)
- **CFP**: [https://cfp.in.pycon.org/2025/cfp](https://cfp.in.pycon.org/2025/cfp)
- **GitHub**: [https://github.com/anistark/pyconindia](https://github.com/anistark/pyconindia)
- **PyPI**: [https://pypi.org/project/pyconindia/](https://pypi.org/project/pyconindia/)
- **Zulip Chat**: [Join our community](https://pyconindia.zulipchat.com/#narrow/stream/282100-2021.2Fpyconindia-team)
- **Twitter**: [@pyconindia](https://twitter.com/pyconindia)

---

Made with 💙 for PyCon India
