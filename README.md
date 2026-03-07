# Homepage Services CLI

A command-line tool for managing [Homepage](https://gethomepage.dev/) configuration files.

## Supported Configuration Files

| Config File | Status | Priority |
|-------------|--------|----------|
| services.yaml | ✅ Implemented | - |
| bookmarks.yaml | 🎯 Implemented | High |
| settings.yaml | 🎯 Implemented | High |
| docker.yaml | 🎯 Implemented | High |
| widgets.yaml | 📋 Planned | Medium |
| proxmox.yaml | 📋 Planned | Medium |
| kubernetes.yaml | 📋 Planned | Medium |
| custom.css | 🔧 Planned | Low |
| custom.js | 🔧 Planned | Low |

## Features

- **Group Management**: List, add, rename, and delete service groups
- **Service Management**: Full CRUD operations for services within groups
- **Service Movement**: Move services between groups
- **Icon Support**: Download PNG icons to `./icons/` with automatic reference generation
- **Flexible Fields**: Set arbitrary service fields using dot-notation
- **Safe Operations**: Automatic `.bak` backups and YAML formatting preservation
- **Validation**: Verify `services.yaml` structure integrity

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (comes with Python)

### Recommended: Install with pipx

**pipx** is the recommended installation method as it creates an isolated environment for the CLI and makes it available system-wide.

```bash
# Install pipx (if not already installed)
pip install --user pipx
pipx ensurepath

# Install homepage-services-cli
pipx install .
```

Or install directly from GitHub:

```bash
pipx install git+https://github.com/beecave-orchestrator/homepage-services-cli.git
```

After installation, the `homepage-services` command will be available from anywhere:

```bash
homepage-services --help
```

#### Troubleshooting pipx

**Command not found after installation:**
- Make sure you've run `pipx ensurepath` and restarted your shell
- Check your PATH includes `~/.local/bin`

**Installation fails:**
- Ensure you have Python 3.10+: `python3 --version`
- Update pipx: `pip install --user --upgrade pipx`

**For more pipx help:** [pipx installation guide](https://pipx.pypa.io/stable/installation/)

---

### Alternative: Install with Poetry or PDM

If you're using Poetry:

```bash
poetry install
poetry run homepage-services --help
```

Or with PDM:

```bash
pdm install
pdm run homepage-services --help
```

---

### Manual Setup (Script Only)

For development or quick testing without installation:

1. Clone or download `homepage_services.py`
2. Install dependencies:

```bash
pip install typer ruamel.yaml requests
```

3. Run directly:

```bash
python homepage_services.py --help
```

## Usage

The CLI follows a hierarchical structure: `homepage-services [command] [subcommand]`

### Getting Help

```bash
homepage-services --help
homepage-services bookmarks --help
homepage-services settings --help
homepage-services docker --help
homepage-services groups --help
homepage-services services --help
```

### Bookmarks Commands

Manage `bookmarks.yaml` for quick links and shortcuts.

#### Validate Bookmarks

```bash
homepage-services bookmarks validate
```

#### List Bookmarks

```bash
# List all bookmarks
homepage-services bookmarks list

# List bookmarks in a specific group
homepage-services bookmarks list --group "Developer"
```

#### Add a Bookmark

```bash
# Basic bookmark with auto-inferred name
homepage-services bookmarks add \
  --url "https://github.com/" \
  --group "Developer"

# Bookmark with custom name and abbreviation
homepage-services bookmarks add \
  --url "https://github.com/" \
  --group "Developer" \
  --name "GitHub" \
  --abbr "GH"

# Bookmark with icon and description
homepage-services bookmarks add \
  --url "https://reddit.com/" \
  --group "Social" \
  --name "Reddit" \
  --icon "reddit.png" \
  --description "The front page of the internet"
```

#### Show Bookmark Details

```bash
homepage-services bookmarks show "Developer" "GitHub"
```

#### Update a Bookmark

```bash
# Update URL
homepage-services bookmarks update "Developer" "GitHub" --url "https://github.com/new"

# Update abbreviation
homepage-services bookmarks update "Developer" "GitHub" --abbr "GH"

# Update description
homepage-services bookmarks update "Social" "Reddit" --description "Updated description"
```

#### Rename a Bookmark

```bash
homepage-services bookmarks rename "Developer" "GitHub" "GitHub Repo"
```

#### Delete a Bookmark

```bash
homepage-services bookmarks delete "Developer" "GitHub"
```

### Settings Commands

Manage `settings.yaml` for global Homepage settings.

#### Validate Settings

```bash
homepage-services settings validate
```

#### Set Global Settings

```bash
# Set title
homepage-services settings set --title "My Awesome Homepage"

# Set theme and color
homepage-services settings set --theme dark --color slate

# Set multiple at once
homepage-services settings set --title "My Homepage" --theme dark --color slate
```

#### Get Settings

```bash
# Get specific setting
homepage-services settings get title

# List all settings
homepage-services settings get
```

#### List All Settings

```bash
homepage-services settings list
```

### Providers Commands (Settings sub-command)

Manage service provider API keys in `settings.yaml`.

#### Add a Provider

```bash
homepage-services settings providers add openweathermap "api-key-here"
```

#### List Providers

```bash
homepage-services settings providers list
```

#### Delete a Provider

```bash
homepage-services settings providers delete openweathermap
```

### Layout Commands (Settings sub-command)

Manage layout configurations for service groups.

#### Set Group Layout

```bash
# Set row layout with 5 columns
homepage-services settings layout set Proxmox --style row --columns 5

# Set only style
homepage-services settings layout set Media --style column
```

#### List Layout Configurations

```bash
homepage-services settings layout list
```

### Docker Commands

Manage `docker.yaml` for Docker container integration.

#### Validate Docker Config

```bash
homepage-services docker validate
```

#### List Docker Instances

```bash
homepage-services docker list
```

#### Add a Docker Instance

```bash
# Add with host and port
homepage-services docker add \
  --name "my-docker" \
  --host "127.0.0.1" \
  --port 2375

# Add with socket
homepage-services docker add \
  --name "other-docker" \
  --socket "/var/run/docker.sock"
```

#### Show Docker Instance Details

```bash
homepage-services docker show "my-docker"
```

#### Update a Docker Instance

```bash
# Update port
homepage-services docker update "my-docker" --port 2376

# Update host
homepage-services docker update "my-docker" --host "192.168.1.100"
```

#### Delete a Docker Instance

```bash
homepage-services docker delete "my-docker"
```

### Services Commands

The CLI follows a hierarchical structure: `homepage-services [command] [subcommand]`

### Getting Help

```bash
homepage-services --help
homepage-services groups --help
homepage-services services --help
```

### Root Commands

#### Validate Configuration

Validate that `services.yaml` matches the expected structure:

```bash
homepage-services validate
```

### Group Commands

#### List All Groups

```bash
homepage-services groups list
```

#### Add a Group

```bash
homepage-services groups add "Infrastructure"
```

#### Rename a Group

```bash
homepage-services groups rename "Infrastructure" "Core Infra"
```

#### Delete a Group

```bash
# Delete empty group
homepage-services groups delete "Media"

# Force delete even if group has services
homepage-services groups delete "Media" --force
```

### Service Commands

#### List All Services

```bash
# List all services (grouped)
homepage-services services list

# List services in a specific group
homepage-services services list --group "Infrastructure"
```

#### Add a Service

Add a service with automatic name inference from URL:

```bash
homepage-services services add \
  --href "http://proxmox.local:8006" \
  --group "Infrastructure"
```

Add a service with a custom name:

```bash
homepage-services services add \
  --href "http://pve.local:8006" \
  --group "Infrastructure" \
  --name "Proxmox VE"
```

Add a service with an icon reference (Material Design Icons or local path):

```bash
# Material Design Icons
homepage-services services add \
  --href "http://radarr.local" \
  --group "Media" \
  --icon "mdi:movie-open"

# Local icon
homepage-services services add \
  --href "http://plex.local" \
  --group "Media" \
  --icon "/icons/plex.png"
```

Add a service with icon download (PNG only):

```bash
homepage-services services add \
  --href "http://jellyfin.local:8096" \
  --group "Media" \
  --name "Jellyfin" \
  --icon-url "https://raw.githubusercontent.com/jellyfin/jellyfin-web/master/branding/SVG/icon-banner-dark.svg"
```

The icon will be downloaded to `./icons/jellyfin.png` and referenced as `/icons/jellyfin.png` in the service configuration.

#### Show Service Details

```bash
homepage-services services show "Proxmox"
```

#### Update a Service

```bash
# Update href
homepage-services services update "Proxmox" --href "http://pve-new.local:8006"

# Update icon reference
homepage-services services update "Plex" --icon "mdi:plex"

# Download new icon
homepage-services services update "Jellyfin" --icon-url "https://new-icon-url.png"
```

#### Rename a Service

```bash
homepage-services services rename "Old Name" "New Name"
```

#### Delete a Service

```bash
homepage-services services delete "Proxmox"
```

#### Move a Service

Move a service from one group to another:

```bash
homepage-services services move "Plex" "Media Apps"
```

#### Set Arbitrary Fields

Set any field in the service configuration using dot-notation:

```bash
# Set description
homepage-services services set-field "Proxmox" "description" "Virtualization platform"

# Set widget type
homepage-services services set-field "Proxmox" "widget.type" "proxmox"

# Set server
homepage-services services set-field "Proxmox" "server" "pve.local"

# Set nested field
homepage-services services set-field "Jellyfin" "widget.fields.enableUser" "true"
```

## YAML Structure

### bookmarks.yaml Structure

This tool expects Homepage's documented `bookmarks.yaml` structure:

```yaml
- Developer:
    - Github:
        - abbr: GH
          href: https://github.com/
- Social:
    - Reddit:
        - icon: reddit.png
          href: https://reddit.com/
          description: The front page of internet
```

### settings.yaml Structure

This tool expects Homepage's documented `settings.yaml` structure:

```yaml
title: My Awesome Homepage
theme: dark
color: slate
layout:
  Proxmox:
    style: row
    columns: 5
providers:
  openweathermap: api-key-here
```

### docker.yaml Structure

This tool expects Homepage's documented `docker.yaml` structure:

```yaml
my-docker:
  host: 127.0.0.1
  port: 2375
other-docker:
  socket: /var/run/docker.sock
```

### services.yaml Structure

This tool expects Homepage's documented `services.yaml` structure:

```yaml
- Group Name:
  - Service Name:
      href: http://example.com
      icon: /icons/service.png
      description: My service
      widget:
        type: custom-widget
        fields:
          key: value
```

The tool preserves your existing YAML formatting using `ruamel.yaml`.

## Safety Features

### Automatic Backups

Every write operation creates a `.bak` backup of your `services.yaml`:

```
services.yaml     # Latest version
services.yaml.bak # Previous version
```

### PNG Validation

When downloading icons via `--icon-url`, the tool validates PNG file signatures and rejects non-PNG downloads.

### Structure Validation

Use the `validate` command to check your `services.yaml` structure:

```bash
homepage-services validate
```

## Development

### Running Tests

To test the tool without modifying your actual `services.yaml`, use the `--services-file` option:

```bash
homepage-services validate --services-file /path/to/test-services.yaml
homepage-services services list --services-file /path/to/test-services.yaml
```

### Custom Icons Directory

By default, icons are downloaded to `./icons/`. You can customize this:

```bash
homepage-services services add \
  --href "http://example.com" \
  --group "Test" \
  --icon-url "http://example.com/icon.png" \
  --icons-dir /custom/icons/path
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

elvee

## Related

- [Bookmarks Configuration](https://gethomepage.dev/configs/bookmarks/)
- [Settings Configuration](https://gethomepage.dev/configs/settings/)
- [Docker Configuration](https://gethomepage.dev/configs/docker/)
- [Services Configuration](https://gethomepage.dev/configs/services/)
- [Homepage Documentation](https://gethomepage.dev/)
- [Homepage GitHub](https://github.com/gethomepage/homepage)
