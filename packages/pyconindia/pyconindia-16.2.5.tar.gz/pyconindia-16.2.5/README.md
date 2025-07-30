# PyCon India

[![PyPI](https://img.shields.io/pypi/v/pyconindia?style=for-the-badge)](https://pypi.org/project/pyconindia/) ![PyPI - Downloads](https://img.shields.io/pypi/dw/pyconindia?style=for-the-badge) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconindia?style=for-the-badge)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  ![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/anistark/pyconindia)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/anistark/pyconindia)

[![Join PyCon India on Zulip](https://img.shields.io/badge/Join-Zulip-blue)](https://pyconindia.zulipchat.com/#narrow/stream/282100-2021.2Fpyconindia-team) [![Follow on Twitter](https://img.shields.io/twitter/follow/pyconindia?style=social&logo=twitter)](https://twitter.com/intent/follow?screen_name=pyconindia)

PyCon India is the largest gathering of Pythonistas in India for the Python programming language. The 13th edition of PyCon India will be taking place online from 17th September to 20th September 2021. With this unique scenario at hand, we plan to make this year's conference bigger, better, and more accessible to Pythonistas all across the world who can watch, participate and share their views right from the comfort of their homes.

## Installation

The `pyconindia` package works both as a **Python library** and a **command-line tool**.

### Install from PyPI (Recommended)

```sh
pip install pyconindia
```

### Install Globally (System-wide)

For system-wide installation that makes the CLI available to all users:

```sh
# Using pip (recommended)
pip install --user pyconindia

# Or install system-wide (requires admin/sudo)
sudo pip install pyconindia

# Using pipx (best practice for CLI tools)
pipx install pyconindia
```

**Note**: We recommend using `pipx` for CLI tools as it installs them in isolated environments while making them globally available.

### Install pipx (if not already installed)

```sh
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
>>> pyconindia.city
'Bengaluru'
>>> pyconindia.venue
'NIMHANS Convention Centre'
>>> pyconindia.location
'NIMHANS Convention Centre, Bengaluru, Karnataka, India'
>>> pyconindia.status
'upcoming'
>>> pyconindia.tickets
'available'
>>> pyconindia.cfp
'Submit your proposal: https://cfp.in.pycon.org/2025/cfp/'

# Using the Conference class
>>> from pyconindia.conference import Conference
>>> conf = Conference()
>>> conf.year()
2025
>>> conf.status(2023)
'over'
>>> conf.tickets(2023)
'sold_out'
>>> conf.schedule(2023)
'View schedule: https://in.pycon.org/2023/schedule/'
```

### As a Command Line Tool

After installation, you can use the CLI commands globally:

#### Basic Usage

```sh
# Show basic conference information
pyconindia

# Or use the shorter alias
inpycon
```

Output:
```
🐍 Welcome to PyCon India CLI!
⏳ Status: Upcoming
🏢 Venue: NIMHANS Convention Centre
📍 Location: NIMHANS Convention Centre, Bengaluru, Karnataka, India
📅 Dates: September 2025 (TBA)
🎫 Tickets: Available
📝 CFP: Submit your proposal: https://cfp.in.pycon.org/2025/cfp/
📋 Schedule: Schedule not prepared yet

Use --help to see all available commands.
```

#### Available Commands

```sh
# Get detailed conference information
pyconindia info
pyconindia info --year 2024        # For specific year
pyconindia info -y 2024             # Short form

# Get conference components
pyconindia city
pyconindia city --year 2024

pyconindia state
pyconindia state --year 2024

pyconindia venue
pyconindia venue --year 2024

pyconindia location
pyconindia location --year 2024

pyconindia month
pyconindia dates
pyconindia dates --year 2024

# Check conference status
pyconindia status
pyconindia status --year 2024

# Get Call for Proposals information
pyconindia cfp
pyconindia cfp --year 2024

# Check ticket availability
pyconindia tickets
pyconindia tickets --year 2024

# Get conference schedule
pyconindia schedule
pyconindia schedule --year 2024

# Get current year
pyconindia year

# Show version
pyconindia version

# Show help
pyconindia --help
```

#### JSON Output

All commands support JSON output for integration with other tools:

```sh
# JSON output
pyconindia --json
pyconindia info --json
pyconindia location --json --year 2024
```

Example JSON output:
```json
{
  "year": 2025,
  "city": "Bengaluru",
  "state": "Karnataka",
  "venue": "NIMHANS Convention Centre",
  "location": "NIMHANS Convention Centre, Bengaluru, Karnataka, India",
  "month": "September",
  "dates": "September 2025 (TBA)",
  "status": "upcoming",
  "cfp": "Submit your proposal: https://cfp.in.pycon.org/2025/cfp/",
  "tickets": "available",
  "schedule": "Schedule not prepared yet",
  "website": "https://in.pycon.org/2025/"
}
```

#### Enhanced Commands

```sh
# Show PyCon India history
pyconindia history
pyconindia history --start-year 2020 --end-year 2025

# Open PyCon India website
pyconindia website
pyconindia open-website --browser        # Opens in default browser

# Check specific year examples
pyconindia info --year 2023             # Past conference
pyconindia info --year 2026             # Future (not planned)
pyconindia info --year 2005             # Pre-historic times
```

Example outputs for different scenarios:

**Past Conference (2023):**
```sh
pyconindia info --year 2023
```
```
🐍 PyCon India 2023
✅ Status: Over
🏢 Venue: Hyderabad International Convention Centre
📍 Location: Hyderabad International Convention Centre, Hyderabad, Telangana, India
📅 Dates: September 29-2, 2023
🎫 Tickets: Sold Out
📝 CFP: Submit your proposal: https://cfp.in.pycon.org/2023/cfp/
📋 Schedule: View schedule: https://in.pycon.org/2023/schedule/
🌐 Website: https://in.pycon.org/2023/
```

**Future Conference (2026):**
```sh
pyconindia info --year 2026
```
```
🐍 PyCon India 2026
🚀 Status: Not Planned
📍 Not Planned Yet! Want to organise? Reach out to mailing list "https://mail.python.org/mailman3/lists/inpycon.python.org/"
📝 Not Planned Yet! Want to organise? Reach out to mailing list "https://mail.python.org/mailman3/lists/inpycon.python.org/"
🌐 Website: https://in.pycon.org/2026/
```

**Pre-historic Times (2005):**
```sh
pyconindia info --year 2005
```
```
🐍 PyCon India 2005
🦕 Status: Prehistoric
📍 Pre-historic times when PyCon India did not exist
📝 Pre-historic times when PyCon India did not exist
🌐 Website: https://in.pycon.org/2005/
```

#### Command Aliases

For convenience, you can use either command name:

```sh
pyconindia info    # Full name
inpycon info       # Short alias
```

## Development

### Local Development Setup

```sh
# Clone the repository
git clone https://github.com/anistark/pyconindia.git
cd pyconindia

# Install in development mode
pip install -e .

# Now you can use the CLI
pyconindia --help
```

### Testing

```sh
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

## Support

If you encounter any issues or have questions, please:

1. Check the [GitHub Issues](https://github.com/anistark/pyconindia/issues)
2. Join our [Zulip community](https://pyconindia.zulipchat.com)
3. Follow us on [Twitter](https://twitter.com/pyconindia)

---

Made with ❤️ by the PyCon India Team
