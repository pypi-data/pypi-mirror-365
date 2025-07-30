This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where comments have been removed, empty lines have been removed, content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: *.json, *.py, *.js, *.ts, *.md
- Files matching these patterns are excluded: node_modules, dist, build, .git
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Code comments have been removed from supported file types
- Empty lines have been removed from all files
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
CHANGELOG.md
example-output.md
mcp-config-tech-spec.md
package.json
template-config.json
```

# Files

## File: CHANGELOG.md
````markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-01-28

### Changed
- **BREAKING**: Streamlined `config` command to handle secrets automatically in a single execution
- The `config` command now processes sensitive values first, then automatically continues with all remaining configuration values
- Removed the need to run `config` command multiple times for complete setup

### Fixed
- Fixed configuration workflow that previously required users to run `mcp-config config` twice
- Eliminated early exit after handling sensitive values
- Added intelligent deduplication to skip already-configured sensitive values in the second phase

### Improved
- Enhanced user experience with seamless single-command configuration process
- Added clear progress indicators showing configuration phases
- Maintained all existing security features (global config protection, automatic sensitive detection)

## [1.2.0] - 2025-01-28

### Added
- Automatic sensitive value detection based on key names containing "password", "secret", "key", "token", "auth", "credential", or "private"
- Global configuration protection with `-g` flag support for `config` and `update-config` commands
- Enhanced security for configuration values with sensitive terms

### Changed
- Updated sensitive detection logic to use both schema-defined sensitivity AND automatic detection
- Enhanced `saveNonSecretToConfig()` function with global config protection
- Added global override flag support to prevent accidental overwrites of system-wide settings

### Security
- All configuration values containing sensitive terms are now automatically stored securely in environment variables
- Global configuration protection prevents accidental overwrites of system-wide settings
- Clear warning messages inform users when global config protection is active

## [1.1.0] - 2025-01-28

### Added
- Initial implementation of MCP configuration management
- Schema-based configuration validation using Convict
- Support for sensitive value handling via environment variables
- Client-specific configuration distribution
- Commands: `config`, `config-secrets`, `get-config`, `update-config`

### Features
- Dynamic schema loading from `template-config.json` or package.json specified path
- Automatic client configuration distribution to VS Code, Cursor, and other supported clients
- Environment variable integration for sensitive data
- Interactive configuration prompts with current value display

## [1.0.0] - 2025-01-28

### Added
- Initial release of mcp-config CLI tool
- Basic configuration management functionality
````

## File: example-output.md
````markdown
# Example Output with Environment Variable References

## What the user sees when running `mcp-config config`:

```
Starting MCP-Config setup...

The application environment. (env) [Current: Not set]: development
The MCP (Model Context Protocol) server port. (mcp.port) [Current: Not set]: 3000
The MCP server host address. (mcp.host) [Current: Not set]: 127.0.0.1
Connection timeout in milliseconds. (mcp.timeout) [Current: Not set]: 30000
The API key for external services. (api.key) [Current: Not set]: sk-1234567890abcdef
🔐 Secret API_KEY saved to .env file as environment variable.
The API secret for external services. (api.secret) [Current: Not set]: secret_xyz123
🔐 Secret API_SECRET saved to .env file as environment variable.

Select target clients (comma-separated, e.g., VS Code, Cursor) [Available: VS Code, Claude Code, Claude Desktop, Cursor] [Current: ]: VS Code, Cursor

Distributing configurations to selected clients...
Created directory for VS Code: C:\Users\User\AppData\Roaming\Code\User
✅ Successfully wrote configuration for VS Code to C:\Users\User\AppData\Roaming\Code\User\mcp-config.json
   (Secrets referenced as environment variables: ${VARIABLE_NAME})
Created directory for Cursor: C:\Users\User\AppData\Roaming\Cursor\User
✅ Successfully wrote configuration for Cursor to C:\Users\User\AppData\Roaming\Cursor\User\mcp-config.json
   (Secrets referenced as environment variables: ${VARIABLE_NAME})

Configuration process complete.

📋 Environment Variables Information:
──────────────────────────────────────────────────

🔐 Sensitive configuration stored as environment variables:
  • api.key → API_KEY
  • api.secret → API_SECRET

💡 How to update environment variables:

🪟 Windows (Command Prompt):
  set API_KEY=your_value_here
  set API_SECRET=your_value_here

🪟 Windows (PowerShell):
  $env:API_KEY="your_value_here"
  $env:API_SECRET="your_value_here"

🐧 Linux/macOS:
  export API_KEY="your_value_here"
  export API_SECRET="your_value_here"

📄 Or add to your .env file (recommended):
  API_KEY=your_value_here
  API_SECRET=your_value_here

⚠️  Note: Client applications will use ${VARIABLE_NAME} references
   Make sure your clients support environment variable expansion.
──────────────────────────────────────────────────
```

## What gets created:

### .env file:
```
API_KEY=sk-1234567890abcdef
API_SECRET=secret_xyz123
```

### config/default.json:
```json
{
  "env": "development",
  "mcp": {
    "port": 3000,
    "host": "127.0.0.1",
    "timeout": 30000
  },
  "api": {
    "baseUrl": "https://api.example.com"
  },
  "clients": {
    "selected": ["VS Code", "Cursor"]
  }
}
```

### VS Code config (C:\Users\User\AppData\Roaming\Code\User\mcp-config.json):
```json
{
  "env": "development",
  "mcp": {
    "port": 3000,
    "host": "127.0.0.1",
    "timeout": 30000
  },
  "api": {
    "key": "${API_KEY}",
    "secret": "${API_SECRET}",
    "baseUrl": "https://api.example.com"
  },
  "clients": {
    "selected": ["VS Code", "Cursor"]
  }
}
```

### Cursor config (C:\Users\User\AppData\Roaming\Cursor\User\mcp-config.json):
```json
{
  "env": "development",
  "mcp": {
    "port": 3000,
    "host": "127.0.0.1",
    "timeout": 30000
  },
  "api": {
    "key": "${API_KEY}",
    "secret": "${API_SECRET}",
    "baseUrl": "https://api.example.com"
  },
  "clients": {
    "selected": ["VS Code", "Cursor"]
  }
}
```

## Security Benefits:

1. **Secrets are NOT in client config files** - only environment variable references
2. **Client applications get the config they need** with references they can expand
3. **Secrets remain in the .env file** which should be .gitignored
4. **Clear instructions** on how to update environment variables
5. **Cross-platform support** with instructions for all operating systems
````

## File: mcp-config-tech-spec.md
````markdown
# Technical Specification: MCP Server Configuration Tool

**Product Name:** MCP-Config

**Version:** 0.1 (Initial Draft)

---

## 1. Core Technologies & Dependencies

* **Language:** Node.js
* **Deployment:** Client-side script, deployable and installable via npm.
* **Key npm Packages:**
    * `dotenv`: For loading environment variables from `.env` files.
    * `config`: For managing standard configuration files (e.g., development, production environments, handling file-based configurations).
    * `convict`: For defining and validating configuration schemas.

---

## 2. Architecture

* The tool will operate as a standalone Node.js script.
* It will expose a Command Line Interface (CLI) for user interaction.
* Config data will be managed across two primary locations:
    * **Environment Variables:** For sensitive information (secrets like API keys).
    * **Standard Config Files:** For non-sensitive settings (managed by the `config` package).
* The tool will interact with the file system to place configs in client-specific directories.

---

## 3. Config Management

**Important Note:** Commands from this package will not be visible to the end user because the referencing component will mask them, providing a seamless integration experience.

* **Schema Definition:**
    * Each MCP project consuming this package will define its specific config schema.
    * This schema will be stored in a JSON file, typically named `template-config.json`, located within the consuming project's directory.
    * The `convict` package will be used to load and validate this schema, ensuring config integrity.
* **Secret Handling:**
    * The tool will intelligently identify sensitive data (e.g., based on key names or explicit tagging in the schema, TBD).
    * Any config values containing the terms "password", "secret", "key", or similar will be stored securely automatically.
    * Sensitive data will be prompted for and stored as environment variables.
    * Persistence of environment variables will be managed by writing to `.env` files in appropriate locations (e.g., user's home directory, or specific project locations, with `.gitignore` recommendations).
    * **Security Note:** While storing in `.env` files is better than hardcoding, the inherent security limitations of client-side secret storage (as discussed) persist. Users will be advised on best practices or the need for a backend proxy for true security.
* **Standard Config:**
    * Non-secret config items will be stored in JSON files, managed by the `config` package.
    * The `config` package's hierarchical capabilities will be leveraged for environment-specific settings (e.g., `default.json`, `development.json`).

---

## 4. Commands & Functionality

* ### `config` Command
    * **User Prompting:** Interactively prompt the user for config values based on the loaded schema (`template-config.json`).
    * **Smart Placement:** Based on the schema definition or internal logic, differentiate between secrets and standard settings.
    * **Secret Storage:** Write identified secrets to environment variables (persisted via `.env` files).
    * **Standard Config Storage:** Write non-secret settings to standard config files (managed by `config`).
    * **Global Config Protection:** If there is a global config already present, the command will not change it unless there is a `-g` flag provided with the command.
    * **Target Client Detection/Prompting:**
        * Upon execution, check if target clients (where configs should be placed) are already defined.
        * If no target clients are specified, prompt the user to select from a predefined list.
        * Initially Supported Target Clients: VS Code, VS Code Desktop, ChatGPT, Cursor, Blotatoad.

* ### `get config` Command
    * **All Configs:** If called without arguments, display all loaded config items.
    * **Location Indicator:** For each item, clearly indicate its source (e.g., "Environment Variable", "config.json", "user home directory").
    * **Specific Config:** If called with a key name (e.g., `get config API_KEY`), display only the value and source for that specific item.

* ### `update config` Command
    * **Interactive Update:** Allow users to modify existing config values.
    * **Smart Placement:** Adhere to the same secret/standard differentiation and storage logic as the `config` command.
    * **Secure Storage:** Any config values containing the terms "password", "secret", "key", or similar will be stored securely automatically.
    * **Global Config Protection:** If there is a global config already present, the command will not modify it unless the `-g` flag is specified.
    * **Target Client Check:** Re-prompt for target clients if none are defined, ensuring config is updated for relevant applications.

* ### Client Config Sharing / Smart Config Placement
    * The tool will integrate with the file system to place generated config artifacts (e.g., specific JSON files, snippets for environment variables) into the expected directories of the selected target clients.
    * This will require mapping specific client types (VS Code, ChatGPT, etc.) to their respective config file paths and formats.

---
````

## File: package.json
````json
{
  "name": "@devjoy-digital/mcp-config",
  "version": "1.3.0",
  "main": "src/index.js",
  "bin": {
    "mcp-config": "src/index.js"
  },
  "scripts": {
    "test": "jest"
  },
  "publishConfig": {
    "access": "public"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/Devjoy-digital/mcp-config.git"
  },
  "keywords": [],
  "author": "Devjoy Digital",
  "license": "ISC",
  "bugs": {
    "url": "https://github.com/Devjoy-digital/mcp-config/issues"
  },
  "homepage": "https://github.com/Devjoy-digital/mcp-config#readme",
  "description": "",
  "dependencies": {
    "commander": "^14.0.0",
    "config": "^4.1.0",
    "convict": "^6.2.4",
    "dotenv": "^17.2.1",
    "yargs": "^18.0.0"
  },
  "devDependencies": {
    "jest": "^30.0.5"
  }
}
````

## File: template-config.json
````json
{
  "env": {
    "doc": "The application environment.",
    "format": ["production", "development", "test"],
    "default": "development",
    "env": "NODE_ENV"
  },
  "mcp": {
    "properties": {
      "port": {
        "doc": "The MCP (Model Context Protocol) server port.",
        "format": "port",
        "default": 3000,
        "env": "MCP_PORT",
        "sensitive": false
      },
      "host": {
        "doc": "The MCP server host address.",
        "format": "String",
        "default": "127.0.0.1",
        "env": "MCP_HOST",
        "sensitive": false
      },
      "timeout": {
        "doc": "Connection timeout in milliseconds.",
        "format": "Number",
        "default": 30000,
        "env": "MCP_TIMEOUT",
        "sensitive": false
      }
    }
  },
  "api": {
    "properties": {
      "key": {
        "doc": "The API key for external services.",
        "format": "String",
        "default": "",
        "env": "API_KEY",
        "sensitive": true
      },
      "secret": {
        "doc": "The API secret for external services.",
        "format": "String",
        "default": "",
        "env": "API_SECRET",
        "sensitive": true
      },
      "baseUrl": {
        "doc": "Base URL for API endpoints.",
        "format": "String",
        "default": "https://api.example.com",
        "env": "API_BASE_URL",
        "sensitive": false
      }
    }
  },
  "postgres": {
    "properties": {
      "host": {
        "doc": "PostgreSQL server hostname or IP address.",
        "format": "String",
        "default": "localhost",
        "env": "POSTGRES_HOST",
        "sensitive": false
      },
      "port": {
        "doc": "PostgreSQL server port number.",
        "format": "port",
        "default": 5432,
        "env": "POSTGRES_PORT",
        "sensitive": false
      },
      "database": {
        "doc": "PostgreSQL database name to connect to.",
        "format": "String",
        "default": "postgres",
        "env": "POSTGRES_DB",
        "sensitive": false
      },
      "username": {
        "doc": "PostgreSQL username for authentication.",
        "format": "String",
        "default": "postgres",
        "env": "POSTGRES_USER",
        "sensitive": false
      },
      "password": {
        "doc": "PostgreSQL password for authentication.",
        "format": "String",
        "default": "",
        "env": "POSTGRES_PASSWORD",
        "sensitive": true
      },
      "ssl": {
        "doc": "Enable SSL connection to PostgreSQL server.",
        "format": "Boolean",
        "default": false,
        "env": "POSTGRES_SSL",
        "sensitive": false
      },
      "connectionTimeout": {
        "doc": "Connection timeout in milliseconds.",
        "format": "Number",
        "default": 10000,
        "env": "POSTGRES_CONNECTION_TIMEOUT",
        "sensitive": false
      },
      "maxConnections": {
        "doc": "Maximum number of concurrent connections.",
        "format": "Number",
        "default": 10,
        "env": "POSTGRES_MAX_CONNECTIONS",
        "sensitive": false
      }
    }
  },
  "clients": {
    "properties": {
      "selected": {
        "doc": "Selected client applications for configuration sharing.",
        "format": "Array",
        "default": [],
        "env": "MCP_CLIENTS",
        "sensitive": false
      }
    }
  }
}
````
