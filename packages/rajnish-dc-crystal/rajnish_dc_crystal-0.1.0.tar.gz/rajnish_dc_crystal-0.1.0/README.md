# Crystal HR Automation

A Python package to automate Crystal HR punch in/out operations with configurable delays and email notifications.

## Features

- Automated punch in/out with configurable delays
- Email notifications for successful/failed operations
- Configurable via JSON config file
- Command-line interface for easy use
- Production-ready package structure

## Installation

### From PyPI (Recommended)

```bash
pip install rajnish-dc-crystal
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rajnish-dc-crystal.git
   cd rajnish-dc-crystal
   ```

2. Install in development mode:
   ```bash
   pip install -e .[dev]
   ```

## Quick Start

1. Initialize configuration:
   ```bash
   crystal-hr config init
   ```

2. Edit the config file (usually at `~/.config/crystal_hr/config.json`) with your credentials.

3. Perform a punch in:
   ```bash
   crystal-hr punch in --delay 5
   ```

4. Perform a punch out:
   ```bash
   crystal-hr punch out
   ```

## Configuration

The configuration file is stored in `~/.config/crystal_hr/config.json` by default. You can specify a different path using the `--config` option.

Example configuration:

```json
{
    "hr_system": {
        "username": "your_username",
        "password": "your_password",
        "company_id": "1",
        "base_url": "https://desicrewdtrial.crystalhr.com"
    },
    "email": {
        "gmail_user": "your.email@gmail.com",
        "gmail_app_password": "your_app_password",
        "recipient_email": "recipient@example.com"
    },
    "behavior": {
        "default_delay_minutes": 0,
        "random_delay_max_minutes": 0
    }
}
```

## Usage

### Punch In/Out

```bash
# Punch in with a 5-minute delay
crystal-hr punch in --delay 5

# Punch out immediately
crystal-hr punch out
```

### Configuration Management

```bash
# Initialize a new config file
crystal-hr config init

# Show current configuration
crystal-hr config show
```

## Development

### Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Disclaimer

This software is provided as-is, without any warranties. Use it responsibly and in compliance with your organization's policies.
