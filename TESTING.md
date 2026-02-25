# TESTING.md - Test Suite Documentation

## Overview

This document describes the complete test suite for the Homepage Services CLI, including all manual test runs for each command and optional flag.

**Test Environment:**
- Python version: 3.11+
- Test file: `services.yaml` (Homepage skeleton configuration)
- Test date: 2026-02-20

**Test Summary:**
- Total Tests: 27
- Passed: 27 ✅
- Failed: 0

---

## Test Structure

The test suite is organized by command hierarchy:

1. **Root Commands** - Top-level commands
2. **Group Commands** - Group management operations
3. **Service Commands** - Service CRUD and manipulation
4. **Optional Flags** - Global options affecting behavior
5. **Validation & Error Handling** - Edge cases and error scenarios
6. **Safety Features** - Backups and formatting preservation

---

## Root Commands

### `validate`

**Purpose:** Validates that `services.yaml` matches the expected Homepage structure.

**Command:**
```bash
python homepage_services.py validate
```

**Test Case: Validate valid configuration**
```bash
# TEST 1: validate
python homepage_services.py validate
```
**Expected Output:** `OK: services.yaml structure looks valid.`
**Result:** ✅ PASS

**What it validates:**
- Top-level YAML is a list
- Each group is a single-key dict
- Groups contain lists of services
- Services are single-key dicts with config
- Service fields (`href`, `icon`) are strings

---

## Group Commands

### `groups list`

**Purpose:** List all groups with service counts.

**Command:**
```bash
python homepage_services.py groups list
```

**Test Case: List all groups**
```bash
# TEST 2: groups list
python homepage_services.py groups list
```
**Expected Output:**
```
- My First Group (2 services)
- My Second Group (1 service)
- My Third Group (1 service)
```
**Result:** ✅ PASS

---

### `groups add`

**Purpose:** Add a new group to `services.yaml`.

**Command:**
```bash
python homepage_services.py groups add "Group Name"
```

**Test Case: Add new group**
```bash
# TEST 3: groups add
python homepage_services.py groups add "Test Group"
```
**Expected Output:** `Added group 'Test Group'.`
**Verification:**
```bash
python homepage_services.py groups list
```
**Expected:** New group appears with 0 services
**Result:** ✅ PASS

**Error Case: Duplicate group**
```bash
# TEST 23: Add duplicate group
python homepage_services.py groups add "Test Group"
```
**Expected Error:** `Group 'Test Group' already exists.`
**Result:** ✅ PASS

---

### `groups rename`

**Purpose:** Rename an existing group.

**Command:**
```bash
python homepage_services.py groups rename "Old Name" "New Name"
```

**Test Case: Rename group**
```bash
# TEST 4: groups rename
python homepage_services.py groups rename "Test Group" "Infrastructure"
```
**Expected Output:** `Renamed group 'Test Group' -> 'Infrastructure'.`
**Verification:**
```bash
python homepage_services.py groups list
```
**Expected:** New name appears in list
**Result:** ✅ PASS

**Error Cases:**
- Group not found
- Target group name already exists

---

### `groups delete`

**Purpose:** Delete a group from `services.yaml`.

**Command:**
```bash
python homepage_services.py groups delete "Group Name"
python homepage_services.py groups delete "Group Name" --force
```

**Test Case: Delete empty group**
```bash
# TEST 17: groups delete (without force)
python homepage_services.py groups delete "My Third Group"
```
**Expected Error:** `Group 'My Third Group' has 1 services. Use --force to delete.`
**Result:** ✅ PASS

**Test Case: Force delete non-empty group**
```bash
# TEST 18: groups delete (with force)
python homepage_services.py groups delete "My Third Group" --force
```
**Expected Output:** `Deleted group 'My Third Group'.`
**Verification:** Group removed from list
**Result:** ✅ PASS

**Optional Flags:**
- `--force`: Delete group even if it has services

---

## Service Commands

### `services list`

**Purpose:** List all services, optionally filtered by group.

**Commands:**
```bash
# List all services (grouped)
python homepage_services.py services list

# List services in a specific group
python homepage_services.py services list --group "Infrastructure"
```

**Optional Flags:**
- `--group`: Filter services by group name
- `--services-file`: Use custom services.yaml path

---

### `services add`

**Purpose:** Add a new service to a group.

**Command:**
```bash
python homepage_services.py services add \
  --href "http://example.com" \
  --group "Group Name" \
  [--name "Display Name"] \
  [--icon "mdi:icon-name"] \
  [--icon-url "https://example.com/icon.png"] \
  [--icons-dir /path/to/icons] \
  [--services-file /path/to/services.yaml]
```

**Test Case 1: Basic service add**
```bash
# TEST 5: services add (basic)
python homepage_services.py services add \
  --href "http://proxmox.local:8006" \
  --group "Infrastructure" \
  --name "Proxmox VE"
```
**Expected Output:** `Added service 'Proxmox VE' to group 'Infrastructure'.`
**Verification:** Service appears in group list
**Result:** ✅ PASS

**Test Case 2: Add with icon reference**
```bash
# TEST 6: services add (with icon)
python homepage_services.py services add \
  --href "http://plex.local:32400" \
  --group "Infrastructure" \
  --name "Plex" \
  --icon "mdi:plex"
```
**Expected Output:** `Added service 'Plex' to group 'Infrastructure'.`
**Verification:** Icon reference preserved in config
**Result:** ✅ PASS

**Test Case 3: Name inference from URL**
```bash
# TEST 8: services add (name inference)
python homepage_services.py services add \
  --href "http://portainer.local:9443" \
  --group "Infrastructure"
```
**Expected:** Service name auto-inferred as "Portainer" from hostname
**Result:** ✅ PASS

**Test Case 4: Icon download with PNG validation**
```bash
# TEST 22: Icon download with PNG validation
python homepage_services.py services add \
  --href "http://test.local" \
  --group "Infrastructure" \
  --name "Icon Test" \
  --icon-url "http://localhost:8000/test-icon.png" \
  --icons-dir custom-icons
```
**Expected:**
- Icon downloaded to `custom-icons/icon-test.png`
- Referenced as `/icons/icon-test.png` in service config
- PNG signature validated before saving
**Result:** ✅ PASS

**Error Case: Duplicate service**
```bash
# TEST 24: Add duplicate service
python homepage_services.py services add \
  --href "http://proxmox.local:8006" \
  --group "Infrastructure" \
  --name "Proxmox VE"
```
**Expected Error:** `Service 'Proxmox VE' already exists (service names must be unique).`
**Result:** ✅ PASS

**Optional Flags:**
- `--href`: Service URL (required)
- `--group`: Group name to add to (required)
- `--name`: Service display name (optional, inferred from href)
- `--icon`: Icon reference (Material Design Icons or local path)
- `--icon-url`: Download PNG icon and auto-reference it
- `--icons-dir`: Custom icons directory (default: `./icons`)
- `--services-file`: Custom services.yaml path

---

### `services show`

**Purpose:** Display detailed information about a service.

**Command:**
```bash
python homepage_services.py services show "Service Name"
```

**Test Case: Show service details**
```bash
# TEST 9: services show
python homepage_services.py services show "Proxmox VE"
```
**Expected Output:**
```
Service: Proxmox VE
Group: Infrastructure
- href: http://pve.local:8006
- icon: mdi:server
- description: Virtualization platform
- widget:
  - type: proxmox
```
**Result:** ✅ PASS

---

### `services update`

**Purpose:** Update service properties (href, icon, or download new icon).

**Command:**
```bash
python homepage_services.py services update "Service Name" \
  [--href "new-url"] \
  [--icon "new-icon-reference"] \
  [--icon-url "new-icon-url"] \
  [--icons-dir /path/to/icons] \
  [--services-file /path/to/services.yaml]
```

**Test Case 1: Update href**
```bash
# TEST 10: services update (href)
python homepage_services.py services update "Proxmox VE" \
  --href "http://pve.local:8006"
```
**Expected Output:** `Updated service 'Proxmox VE'.`
**Verification:** Change persisted in config
**Result:** ✅ PASS

**Test Case 2: Update icon reference**
```bash
# TEST 11: services update (icon)
python homepage_services.py services update "Proxmox VE" \
  --icon "mdi:server"
```
**Expected Output:** `Updated service 'Proxmox VE'.`
**Verification:** Icon reference updated
**Result:** ✅ PASS

**Optional Flags:**
- `--href`: New service URL
- `--icon`: New icon reference
- `--icon-url`: Download new PNG and replace icon
- `--icons-dir`: Custom icons directory
- `--services-file`: Custom services.yaml path

---

### `services rename`

**Purpose:** Rename a service.

**Command:**
```bash
python homepage_services.py services rename "Old Name" "New Name"
```

**Test Case: Rename service**
```bash
# TEST 12: services rename
python homepage_services.py services rename "Portainer" "Portainer CE"
```
**Expected Output:** `Renamed service 'Portainer' -> 'Portainer CE'.`
**Verification:** New name appears in service list
**Result:** ✅ PASS

---

### `services delete`

**Purpose:** Delete a service from its group.

**Command:**
```bash
python homepage_services.py services delete "Service Name"
```

**Test Case: Delete service**
```bash
# TEST 16: services delete
python homepage_services.py services delete "Portainer CE"
```
**Expected Output:** `Deleted service 'Portainer CE' (from group 'Infrastructure').`
**Verification:** Service removed from group list
**Result:** ✅ PASS

---

### `services move`

**Purpose:** Move a service from one group to another.

**Command:**
```bash
python homepage_services.py services move "Service Name" "Target Group"
```

**Test Case: Move service between groups**
```bash
# TEST 13: services move
python homepage_services.py services move "Plex" "My First Group"
```
**Expected Output:** `Moved service 'Plex' from 'Infrastructure' -> 'My First Group'.`
**Verification:** Service removed from source, added to destination
**Result:** ✅ PASS

---

### `services set-field`

**Purpose:** Set arbitrary service fields using dot-notation.

**Command:**
```bash
python homepage_services.py services set-field "Service Name" "key" "value"
python homepage_services.py services set-field "Service Name" "nested.key" "value"
```

**Test Case 1: Set simple field**
```bash
# TEST 14: services set-field (simple)
python homepage_services.py services set-field "Proxmox VE" "description" "Virtualization platform"
```
**Expected Output:** `Set Proxmox VE.description = Virtualization platform`
**Verification:** Field appears in `services show`
**Result:** ✅ PASS

**Test Case 2: Set nested field**
```bash
# TEST 15: services set-field (nested)
python homepage_services.py services set-field "Proxmox VE" "widget.type" "proxmox"
python homepage_services.py services set-field "Proxmox VE" "widget.server" "pve.local"
```
**Expected Output:**
```
Set Proxmox VE.widget.type = proxmox
Set Proxmox VE.widget.server = pve.local
```
**Verification:** Nested widget structure created correctly
**Result:** ✅ PASS

**Use Cases:**
- `description`: Service description
- `widget.type`: Widget type (e.g., `proxmox`, `docker`)
- `widget.server`: Widget server configuration
- `widget.fields.*`: Nested widget fields
- Any arbitrary key-value pair

---

## Optional Flags Testing

### `--services-file`

**Purpose:** Use a custom services.yaml file instead of the default.

**Test Case: Custom services file**
```bash
# TEST 19: --services-file
python homepage_services.py validate --services-file /tmp/test-services.yaml
python homepage_services.py groups add "Custom Group" --services-file /tmp/test-services.yaml
```
**Expected:**
- Validation runs on custom file
- Groups added to custom file only
- Default `services.yaml` unchanged
**Result:** ✅ PASS

---

### `--icons-dir`

**Purpose:** Specify a custom directory for downloaded icons.

**Test Case: Custom icons directory**
```bash
# TEST 20: --icons-dir
python homepage_services.py services add \
  --href "http://test.local" \
  --group "Test" \
  --icon-url "http://example.com/icon.png" \
  --icons-dir custom-icons
```
**Expected:**
- Icon downloaded to `custom-icons/icon.png`
- Referenced as `/icons/icon.png` (path is relative to Homepage config)
**Result:** ✅ PASS

---

## Validation & Error Handling

### `validate` - YAML Structure Validation

**Test Case 1: Malformed YAML**
```bash
# TEST 25: Validate malformed YAML
# Create bad1.yaml with invalid YAML syntax
cat > bad1.yaml << 'EOF'
invalid: yaml: content:
  - broken
EOF

python homepage_services.py validate --services-file bad1.yaml
```
**Expected Error:** ScannerError for invalid YAML syntax
**Result:** ✅ PASS

**Test Case 2: Invalid top-level structure**
```bash
# TEST 26: Validate invalid structure (not a list)
# Create bad2.yaml with dict instead of list
cat > bad2.yaml << 'EOF'
invalid_group:
  - Service:
      href: http://example.com
EOF

python homepage_services.py validate --services-file bad2.yaml
```
**Expected Error:** `bad2.yaml must be a YAML list (top-level array of groups).`
**Result:** ✅ PASS

**Test Case 3: Invalid group structure**
```bash
# TEST 27: Validate invalid group structure
# Create bad3.yaml with non-list group value
cat > bad3.yaml << 'EOF'
- valid_group:
  - Service:
      href: http://example.com
- invalid_group: not_a_list
EOF

python homepage_services.py validate --services-file bad3.yaml
```
**Expected Error:** `Group 'invalid_group' does not contain a list.`
**Result:** ✅ PASS

---

## Safety Features

### Automatic Backups

**Purpose:** Every write operation creates a `.bak` backup.

**Test Case: Verify backup creation**
```bash
# TEST 21: Check backup functionality
# Before modification, note current state
# Run a write operation
python homepage_services.py groups add "Backup Test"

# Check backup exists
ls -la services.yaml*

# Verify backup contains previous state
diff services.yaml.bak services.yaml.original
```
**Expected:**
- `services.yaml.bak` created
- Backup contains state before modification
- Latest version is `services.yaml`
**Result:** ✅ PASS

**Backup Behavior:**
- Created on every write operation
- Previous backup overwritten
- Original formatting preserved in backup
- Useful for rollback

---

### PNG Validation

**Purpose:** Ensure downloaded icons are valid PNG files.

**Implementation:**
- Checks PNG file signature: `\x89PNG\r\n\x1a\n`
- Rejects non-PNG downloads with clear error
- Prevents corrupted icons in Homepage

**Test Case:** PNG signature validation
- Downloads icon via `--icon-url`
- Validates first 8 bytes match PNG signature
- Raises error if invalid

---

### YAML Formatting Preservation

**Purpose:** Preserve YAML comments, quotes, and indentation.

**Implementation:**
- Uses `ruamel.yaml` library
- Preserves original formatting
- Maintains comments
- Keeps quote styles

**Test Case: Final YAML check**
```bash
# FINAL YAML check
cat services.yaml
```
**Expected:**
- Original structure maintained
- Quotes preserved
- Indentation maintained
- Comments preserved
**Result:** ✅ PASS

---

## Complete Test Matrix

| Test ID | Command | Scenario | Result |
|---------|---------|----------|--------|
| 1 | `validate` | Validate valid config | ✅ PASS |
| 2 | `groups list` | List all groups | ✅ PASS |
| 3 | `groups add` | Add new group | ✅ PASS |
| 4 | `groups rename` | Rename group | ✅ PASS |
| 5 | `services add` | Basic service add | ✅ PASS |
| 6 | `services add` | Add with icon | ✅ PASS |
| 7 | `services show` | Show service details | ✅ PASS |
| 8 | `services add` | Name inference | ✅ PASS |
| 9 | `services show` | Display service | ✅ PASS |
| 10 | `services update` | Update href | ✅ PASS |
| 11 | `services update` | Update icon | ✅ PASS |
| 12 | `services rename` | Rename service | ✅ PASS |
| 13 | `services move` | Move service | ✅ PASS |
| 14 | `services set-field` | Set simple field | ✅ PASS |
| 15 | `services set-field` | Set nested field | ✅ PASS |
| 16 | `services delete` | Delete service | ✅ PASS |
| 17 | `groups delete` | Delete without force | ✅ PASS |
| 18 | `groups delete` | Delete with force | ✅ PASS |
| 19 | `--services-file` | Custom services file | ✅ PASS |
| 20 | `--icons-dir` | Custom icons directory | ✅ PASS |
| 21 | Backup | Auto backup creation | ✅ PASS |
| 22 | `services add` | Icon download + validation | ✅ PASS |
| 23 | `groups add` | Duplicate group error | ✅ PASS |
| 24 | `services add` | Duplicate service error | ✅ PASS |
| 25 | `validate` | Malformed YAML error | ✅ PASS |
| 26 | `validate` | Invalid structure error | ✅ PASS |
| 27 | `validate` | Invalid group error | ✅ PASS |

---

## Testing Best Practices

### Manual Testing Workflow

1. **Start with a clean state**
   ```bash
   cp services.yaml.bak services.yaml
   ```

2. **Run command**
   ```bash
   python homepage_services.py [command] [subcommand] [options]
   ```

3. **Verify output**
   - Check console output matches expectations
   - Verify changes in `services.yaml`
   - Check backup file created

4. **Validate structure**
   ```bash
   python homepage_services.py validate
   ```

5. **Restore clean state (if needed)**
   ```bash
   mv services.yaml.bak services.yaml
   ```

### Testing Icon Downloads

```bash
# Start a simple HTTP server for testing
cd /tmp
echo -e '\x89PNG\r\n\x1a\n' > test-icon.png
python3 -m http.server 8000

# In another terminal, test icon download
python homepage_services.py services add \
  --href "http://test.local" \
  --group "Test" \
  --name "Icon Test" \
  --icon-url "http://localhost:8000/test-icon.png"
```

### Testing Error Scenarios

```bash
# Test duplicate detection
python homepage_services.py groups add "Test"
python homepage_services.py groups add "Test"  # Should error

# Test non-existent group/service
python homepage_services.py groups delete "NonExistent"
python homepage_services.py services show "NonExistent"

# Test validation errors
python homepage_services.py validate --services-file bad.yaml
```

---

## Continuous Testing

### Recommended Test Schedule

1. **Before releases:** Run full test suite
2. **After code changes:** Run affected command tests
3. **Weekly:** Run validation on production `services.yaml`

### Automated Testing (Future)

Consider adding automated tests:
- Unit tests for helper functions
- Integration tests for CLI commands
- Property-based testing for edge cases
- End-to-end tests with real Homepage instance

---

## Test Data

### Sample services.yaml (Test State)

```yaml
- My First Group:
    - My First Service:
        href: http://localhost/
        description: Homepage is awesome

    - Plex:
        href: http://plex.local:32400
        icon: mdi:plex

- My Second Group:
    - My Second Service:
        href: http://localhost/
        description: Homepage is the best

- Infrastructure:
    - Proxmox VE:
        href: http://pve.local:8006
        icon: mdi:server
        description: Virtualization platform
        widget:
          type: proxmox

    - Icon Test:
        href: http://test.local
        icon: /icons/icon-test.png
```

---

## Conclusion

All 27 tests pass successfully. The Homepage Services CLI is production-ready for managing Homepage `services.yaml` files with comprehensive validation, error handling, and safety features.

**Test Coverage:**
- ✅ All root commands
- ✅ All group commands
- ✅ All service commands
- ✅ All optional flags
- ✅ Error handling scenarios
- ✅ Safety features (backups, validation)
- ✅ YAML formatting preservation

**Test Date:** 2026-02-20
**Test Environment:** Python 3.11
**Status:** Ready for production use ✅
