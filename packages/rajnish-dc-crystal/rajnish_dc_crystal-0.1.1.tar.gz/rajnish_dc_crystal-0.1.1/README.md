# crystal-hr

[![PyPI](https://img.shields.io/pypi/v/crystal-hr?color=blue)](https://pypi.org/project/crystal-hr/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-0rajnishk%2Frajnish_dc_crystal-blue?logo=github)](https://github.com/0rajnishk/rajnish_dc_crystal)

Automate your CrystalHR punch-in/punch-out with configurable delays and email notifications. Designed for both convenience and privacy, this package offers a simple CLI for regular users and a solid foundation for contributors.

---

## 🚀 For Users

### 1. Installation

Install the latest release directly from PyPI:

```bash
pip install crystal-hr
```

### 2. Initial Configuration

Set up your configuration file with a single command:

```bash
crystal-hr config init
```

This will create a file at:

- **Linux/macOS:** `~/.config/crystal_hr/config.json`
- **Windows:** `C:\Users\<YourUsername>\.config\crystal_hr\config.json`

#### Example Configuration (`config.json`)

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

#### Update the Following Fields

- `hr_system.username`  
- `hr_system.password`  
- `email.gmail_user`  
- `email.gmail_app_password`  
- `email.recipient_email`  

Edit the file in-place with your credentials and settings using any text editor:
- **Linux/macOS:** `nano ~/.config/crystal_hr/config.json`
- **Windows:** Open the file via Notepad or VSCode.

#### Verify Your Configuration

To review your current configuration, run:

```bash
crystal-hr config
```

---

### 3. Usage

#### Basic Commands

- **Punch In:**  
  ```bash
  crystal-hr punch in
  ```
- **Punch Out:**  
  ```bash
  crystal-hr punch out
  ```

#### Add a Delay (Optional)

- Add a fixed delay before action (e.g., 5 minutes):
  ```bash
  crystal-hr punch in --delay 5
  ```
- If `--delay` is not specified, a random delay (1-10 minutes) is applied by default to mimic human-like behavior.

---

### 4. Scheduling with Crontab (Linux/macOS)

Automate your attendance using `crontab`. The built-in random/fixed delay helps avoid robotic timing.

#### Open your crontab editor:

```bash
crontab -e
```

#### Example: Schedule punch in at 8:00 AM and punch out at 6:00 PM

```
0 8 * * * crystal-hr punch in
0 18 * * * crystal-hr punch out
```

> **Tip:** No need to manually specify a delay unless you want a fixed value; the tool will select a random delay by default.

#### Advanced: Explicit Fixed Delay

```
0 8 * * * crystal-hr punch in --delay 7
0 18 * * * crystal-hr punch out --delay 5
```

#### Windows Task Scheduler

On Windows, use the Task Scheduler to run similar commands at your preferred times.

---

## 🤝 For Contributors

We welcome contributions to enhance features, improve documentation, and fix bugs.

### Developing Locally

1. **Fork** this repository:  
   [https://github.com/0rajnishk/rajnish_dc_crystal](https://github.com/0rajnishk/rajnish_dc_crystal)

2. **Clone your fork:**
   ```bash
   git clone https://github.com/<your-username>/rajnish_dc_crystal.git
   cd rajnish_dc_crystal
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up a virtual environment** (recommended).

5. **Submit a Pull Request** with a clear description of your changes.

### Guidelines

- Ensure code is formatted with [PEP8](https://pep8.org/) standards.
- Add or update tests as appropriate.
- Document new features for users and developers.

---

## ℹ️ Support & Community

- [GitHub Issues](https://github.com/0rajnishk/rajnish_dc_crystal/issues) for bug reports and feature requests.
- PRs are always welcome—please open an issue to discuss significant changes first.

---

**Project Homepage:**  
[https://github.com/0rajnishk/rajnish_dc_crystal](https://github.com/0rajnishk/rajnish_dc_crystal)

---