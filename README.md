# Homepage Services CLI

A command-line tool for managing [Homepage](https://gethomepage.dev/) `services.yaml` configuration files.

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
- pip

### Install Dependencies

```bash
pip install typer ruamel.yaml requests
```

### Setup

1. Clone or download `homepage_services.py`
2. Place it in the same directory as your `services.yaml` file (typically your Homepage config directory)
3. Make it executable (optional):

```bash
chmod +x homepage_services.py
```

## Usage

The CLI follows a hierarchical structure: `homepage_services.py [command] [subcommand]`

### Getting Help

```bash
python homepage_services.py --help
python homepage_services.py groups --help
python homepage_services.py services --help
```

### Root Commands

#### Validate Configuration

Validate that `services.yaml` matches the expected structure:

```bash
python homepage_services.py validate
```

### Group Commands

#### List All Groups

```bash
python homepage_services.py groups list
```

#### Add a Group

```bash
python homepage_services.py groups add "Infrastructure"
```

#### Rename a Group

```bash
python homepage_services.py groups rename "Infrastructure" "Core Infra"
```

#### Delete a Group

```bash
# Delete empty group
python homepage_services.py groups delete "Media"

# Force delete even if group has services
python homepage_services.py groups delete "Media" --force
```

### Service Commands

#### List All Services

```bash
# List all services (grouped)
python homepage_services.py services list

# List services in a specific group
python homepage_services.py services list --group "Infrastructure"
```

#### Add a Service

Add a service with automatic name inference from URL:

```bash
python homepage_services.py services add \
  --href "http://proxmox.local:8006" \
  --group "Infrastructure"
```

Add a service with a custom name:

```bash
python homepage_services.py services add \
  --href "http://pve.local:8006" \
  --group "Infrastructure" \
  --name "Proxmox VE"
```

Add a service with an icon reference (Material Design Icons or local path):

```bash
# Material Design Icons
python homepage_services.py services add \
  --href "http://radarr.local" \
  --group "Media" \
  --icon "mdi:movie-open"

# Local icon
python homepage_services.py services add \
  --href "http://plex.local" \
  --group "Media" \
  --icon "/icons/plex.png"
```

Add a service with icon download (PNG only):

```bash
python homepage_services.py services add \
  --href "http://jellyfin.local:8096" \
  --group "Media" \
  --name "Jellyfin" \
  --icon-url "https://raw.githubusercontent.com/jellyfin/jellyfin-web/master/branding/SVG/icon-banner-dark.svg"
```

The icon will be downloaded to `./icons/jellyfin.png` and referenced as `/icons/jellyfin.png` in the service configuration.

#### Show Service Details

```bash
python homepage_services.py services show "Proxmox"
```

#### Update a Service

```bash
# Update href
python homepage_services.py services update "Proxmox" --href "http://pve-new.local:8006"

# Update icon reference
python homepage_services.py services update "Plex" --icon "mdi:plex"

# Download new icon
python homepage_services.py services update "Jellyfin" --icon-url "https://new-icon-url.png"
```

#### Rename a Service

```bash
python homepage_services.py services rename "Old Name" "New Name"
```

#### Delete a Service

```bash
python homepage_services.py services delete "Proxmox"
```

#### Move a Service

Move a service from one group to another:

```bash
python homepage_services.py services move "Plex" "Media Apps"
```

#### Set Arbitrary Fields

Set any field in the service configuration using dot-notation:

```bash
# Set description
python homepage_services.py services set-field "Proxmox" "description" "Virtualization platform"

# Set widget type
python homepage_services.py services set-field "Proxmox" "widget.type" "proxmox"

# Set server
python homepage_services.py services set-field "Proxmox" "server" "pve.local"

# Set nested field
python homepage_services.py services set-field "Jellyfin" "widget.fields.enableUser" "true"
```

## YAML Structure

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
python homepage_services.py validate
```

## Development

### Running Tests

To test the tool without modifying your actual `services.yaml`, use the `--services-file` option:

```bash
python homepage_services.py validate --services-file /path/to/test-services.yaml
python homepage_services.py services list --services-file /path/to/test-services.yaml
```

### Custom Icons Directory

By default, icons are downloaded to `./icons/`. You can customize this:

```bash
python homepage_services.py services add \
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

- [Homepage Documentation](https://gethomepage.dev/)
- [Homepage GitHub](https://github.com/gethomepage/homepage)
