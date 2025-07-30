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
CLAUDE.md
README.md
```

# Files

## File: CLAUDE.md
````markdown
# 🔄 CLAUDE.md - cctx Project Documentation

## 📋 Project Overview

**cctx** (Claude Context) is a fast, secure, and intuitive command-line tool for managing multiple Claude Code `settings.json` configurations. Built with Rust for maximum performance and reliability.

## 🏗️ Architecture

### 🎯 Core Concept
- **🔧 Context**: A saved Claude Code configuration stored as a JSON file
- **⚡ Current Context**: The active configuration (`~/.claude/settings.json`)
- **📁 Context Storage**: All contexts are stored in `~/.claude/settings/` as individual JSON files
- **📊 State Management**: Current and previous context tracked in `~/.claude/settings/.cctx-state.json`

### 📁 File Structure
```
📁 ~/.claude/
├── ⚙️ settings.json           # Current active context (managed by cctx)
└── 📁 settings/
    ├── 💼 work.json          # Work context
    ├── 🏠 personal.json      # Personal context
    ├── 🚀 project-alpha.json # Project-specific context
    └── 🔒 .cctx-state.json   # Hidden state file (tracks current/previous)
```

### 🎯 Key Design Decisions
1. **File-based contexts**: Each context is a separate JSON file, making manual management possible
2. **Simple naming**: Filename (without .json) = context name
3. **Atomic operations**: Context switching is done by copying files
4. **Hidden state file**: Prefixed with `.` to hide from context listings
5. **Predictable UX**: Default behavior always uses user-level contexts for consistency
6. **Progressive disclosure**: Helpful hints show when project/local contexts are available

## 🎯 Command Reference

### 🚀 Basic Commands
- `cctx` - List contexts (defaults to user-level, shows helpful hints)
- `cctx <name>` - Switch to context
- `cctx -` - Switch to previous context

### 🏗️ Settings Level Management
- `cctx` - Default: user-level contexts (`~/.claude/settings.json`)
- `cctx --in-project` - Project-level contexts (`./.claude/settings.json`)
- `cctx --local` - Local project contexts (`./.claude/settings.local.json`)

### 🛠️ Management Commands
- `cctx -n <name>` - Create new context from current settings
- `cctx -d <name>` - Delete context
- `cctx -r <old> <new>` - Rename context
- `cctx -c` - Show current context name
- `cctx -e [name]` - Edit context with $EDITOR
- `cctx -s [name]` - Show context content
- `cctx -u` - Unset current context

### 📥📤 Import/Export
- `cctx --export <name>` - Export to stdout
- `cctx --import <name>` - Import from stdin

## Implementation Details

### Language & Dependencies
- **Language**: Rust (edition 2021)
- **Key Dependencies**:
  - `clap` - Command-line argument parsing
  - `serde`/`serde_json` - JSON serialization
  - `dialoguer` - Interactive prompts
  - `colored` - Terminal colors
  - `anyhow` - Error handling
  - `dirs` - Platform-specific directories

### Error Handling
- Use `anyhow::Result` for all functions that can fail
- Provide clear error messages with context
- Validate context names (no `/`, `.`, `..`, or empty)
- Check for active context before deletion

### 🎨 Interactive Features
1. **fzf integration**: Auto-detect and use if available
2. **Built-in fuzzy finder**: Fallback when fzf not available
3. **Color coding**: Current context highlighted in green
4. **Helpful hints**: Shows available project/local contexts when at user level
5. **Visual indicators**: Emojis for different context levels (👤 User, 📁 Project, 💻 Local)

## 🚀 Release Management

### Simplified Release System

The project uses a streamlined release process with one primary tool:

#### **quick-release.sh** - Primary Release Script

A simple, reliable release script that handles the entire release process:

```bash
# One-command release
./quick-release.sh patch      # 0.1.0 -> 0.1.1
./quick-release.sh minor      # 0.1.0 -> 0.2.0  
./quick-release.sh major      # 0.1.0 -> 1.0.0
```

**What it does:**
1. ✅ Validates git state (clean working tree, on main branch)
2. ✅ Runs quality checks (fmt, clippy, test, build)
3. ✅ Updates version in Cargo.toml
4. ✅ Creates git commit and tag
5. ✅ Pushes to GitHub
6. ✅ Triggers GitHub Actions for:
   - Building release binaries for all platforms
   - Creating GitHub release with artifacts
   - Publishing to crates.io

#### **GitHub Actions Workflows**

**CI Pipeline** (`.github/workflows/ci.yml`):
- Multi-platform testing (Ubuntu, macOS, Windows)
- Rust stable version only
- Format checking, linting, tests
- Security audit
- MSRV (1.81) testing

**Release Pipeline** (`.github/workflows/release.yml`):
- Triggered by version tags (v*.*.*)
- Builds binaries for:
  - Linux x86_64 (glibc and musl)
  - Windows x86_64
  - macOS x86_64 and aarch64
- Creates GitHub release with all artifacts

**Publish Pipeline** (`.github/workflows/publish.yml`):
- Triggered by version tags
- Runs final quality checks
- Publishes to crates.io

#### **Justfile Integration**

For those who prefer `just`:
```bash
just release-patch    # Same as ./quick-release.sh patch
just release-minor    # Same as ./quick-release.sh minor
just release-major    # Same as ./quick-release.sh major
```

### Release Process

1. **Make your changes and commit them**
2. **Run the release command:**
   ```bash
   ./quick-release.sh patch  # or minor/major
   ```
3. **Confirm when prompted**
4. **Monitor progress at:** https://github.com/nwiizo/cctx/actions
5. **Release appears at:** https://github.com/nwiizo/cctx/releases

### Quality Requirements

All releases automatically check:
- ✅ `cargo fmt --check` (code formatting)
- ✅ `cargo clippy -- -D warnings` (linting)
- ✅ `cargo test` (unit tests)
- ✅ `cargo build --release` (release build)
- ✅ Git working directory is clean
- ✅ On main branch and up-to-date with origin

### Removed Tools

To keep things simple, we've removed:
- ❌ `release.sh` - Too complex with many features
- ❌ `release-cargo.sh` - Redundant cargo-release wrapper
- ❌ `release-plz` - GitHub Actions permission issues

### CI/CD Configuration

**Required Secrets:**
- `CARGO_REGISTRY_TOKEN`: For crates.io publishing

**Setting up CARGO_REGISTRY_TOKEN:**
1. **Get your crates.io API token:**
   ```bash
   # Login to crates.io (opens browser)
   cargo login
   # Or visit https://crates.io/me and click "New Token"
   ```
2. **Add to GitHub repository secrets:**
   
   **Option A: Via GitHub Web UI**
   - Go to your repository on GitHub
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CARGO_REGISTRY_TOKEN`
   - Value: Your crates.io API token
   - Click "Add secret"
   
   **Option B: Via GitHub CLI**
   ```bash
   # Install GitHub CLI if needed: https://cli.github.com
   # First, save your token to a file (more secure than command line)
   echo "YOUR_CRATES_IO_TOKEN" > ~/.cargo/crates-token
   
   # Add the secret to your repository
   gh secret set CARGO_REGISTRY_TOKEN < ~/.cargo/crates-token
   
   # Clean up the token file
   rm ~/.cargo/crates-token
   ```

**Key Settings:**
- MSRV: Rust 1.81
- Platforms: Linux, macOS, Windows
- Release formats: Binary executables + crates.io package

## Development Guidelines

### Before Making Changes

1. **Understand the current implementation**:
   ```bash
   cargo check
   cargo clippy
   ```

2. **Run existing tests** (if any):
   ```bash
   cargo test
   ```

3. **Use development tools**:
   ```bash
   just setup                   # Setup dev environment
   just check                   # Run all checks
   ```

### Making Changes

1. **Always run linting** before committing:
   ```bash
   cargo clippy -- -D warnings
   ```

2. **Format code** using Rust standards:
   ```bash
   cargo fmt
   ```

3. **Test thoroughly**:
   - Test basic operations: create, switch, delete contexts
   - Test edge cases: empty names, special characters, missing files
   - Test interactive mode with and without fzf
   - Test on different platforms if possible

4. **Validate JSON handling**:
   - Ensure invalid JSON files are rejected
   - Preserve JSON formatting when possible
   - Handle missing or corrupted state files gracefully

### Testing Checklist

When testing changes, verify:

- [ ] `cctx` lists all contexts correctly
- [ ] `cctx <name>` switches context
- [ ] `cctx -` returns to previous context
- [ ] `cctx -n <name>` creates new context
- [ ] `cctx -d <name>` deletes context (not if current)
- [ ] `cctx -r <old> <new>` renames context
- [ ] Interactive mode works (both fzf and built-in)
- [ ] Error messages are clear and helpful
- [ ] State persistence works across sessions
- [ ] Hidden files are excluded from listings

### Common Pitfalls

1. **File permissions**: Ensure created files have appropriate permissions
2. **Path handling**: Use PathBuf consistently, avoid string manipulation
3. **JSON validation**: Always validate JSON before writing
4. **State consistency**: Update state file atomically

## Future Considerations

### Potential Enhancements
- Context templates/inheritance
- Context validation against Claude Code schema
- Backup/restore functionality
- Context history beyond just previous
- Shell completions

### Compatibility
- Maintain backward compatibility with existing contexts
- Keep command-line interface stable
- Preserve kubectx-like user experience

## Code Quality Standards

1. **Every function should**:
   - Have a clear, single responsibility
   - Return `Result` for fallible operations
   - Include error context with `.context()`

2. **User-facing messages**:
   - Error messages should be helpful and actionable
   - Success messages should be concise
   - Use color coding consistently (green=success, red=error)

3. **File operations**:
   - Always check if directories exist before use
   - Handle missing files gracefully
   - Use atomic operations where possible


## 🎯 UX Design Philosophy

### 🏆 Simplified User Experience (v0.1.1+)

**Core Principle**: **Predictable defaults with explicit overrides**

#### ✅ What We Did Right
- **Removed complex auto-detection** that was confusing users
- **Default always uses user-level** for predictable behavior
- **Clear explicit flags** (`--in-project`, `--local`) when needed
- **Helpful progressive disclosure** - hints when other contexts available
- **Visual clarity** with emojis and condensed information

#### ❌ What We Avoided
- **Complex flag combinations** (`--user`, `--project`, `--local`, `--level`)
- **Unpredictable auto-detection logic** 
- **Verbose technical output** showing file paths
- **Cognitive overhead** from too many options

#### 🎯 UX Goals Achieved
1. **⚡ Speed**: Default behavior is instant and predictable
2. **🧠 Simplicity**: Two explicit flags instead of four confusing ones
3. **🎯 Discoverability**: Helpful hints guide users to advanced features
4. **🔄 Consistency**: Always behaves the same way (user-level default)

### 📝 Usage Patterns

```bash
# 90% of usage - simple and predictable
cctx                    # List user contexts + helpful hints
cctx work              # Switch to work context

# 10% of usage - explicit when needed  
cctx --in-project staging   # Project-specific contexts
cctx --local debug         # Local development contexts
```

## 📚 Notes for AI Assistants

When working on this codebase:

1. **Always run `cargo clippy` and fix warnings** before suggesting code
2. **Test your changes** - don't assume code works
3. **Preserve existing behavior** unless explicitly asked to change it
4. **Follow Rust idioms** and best practices
5. **Keep the kubectx-inspired UX** - simple, fast, intuitive
6. **Maintain predictable defaults** - user should never be surprised
7. **Document any new features** in both code and README
8. **Consider edge cases** - empty states, missing files, permissions
9. **Progressive disclosure** - show advanced features only when relevant

Remember: This tool is about speed and simplicity. Every feature should make context switching faster or easier, not more complex. **Predictability beats cleverness.**
````

## File: README.md
````markdown
# 🔄 cctx - Claude Context Switcher

> ⚡ **Fast and intuitive** way to switch between Claude Code contexts (`~/.claude/settings.json`)

[![Crates.io](https://img.shields.io/crates/v/cctx)](https://crates.io/crates/cctx)
[![CI](https://github.com/nwiizo/cctx/workflows/CI/badge.svg)](https://github.com/nwiizo/cctx/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/rust-1.81%2B-orange.svg)](https://www.rust-lang.org/)

**cctx** (Claude Context) is a kubectx-inspired command-line tool for managing multiple Claude Code configurations. Switch between different permission sets, environments, and settings with a single command.

## ✨ Features

- 🔀 **Instant context switching** - Switch between configurations in milliseconds
- 🎯 **Predictable UX** - Default behavior always uses user-level contexts (no surprises!)
- 🛡️ **Security-first** - Separate permissions for work, personal, and project contexts
- 🎨 **Beautiful CLI** - Colorized output with helpful hints and visual indicators
- 🚀 **Shell completions** - Tab completion for all major shells
- 📦 **Zero dependencies** - Single binary, works everywhere
- 🔄 **Previous context** - Quick switch back with `cctx -`
- 📁 **File-based** - Simple JSON files you can edit manually
- 🎭 **Kubectx-inspired** - Familiar UX for Kubernetes users
- 💡 **Progressive disclosure** - Shows project/local contexts when available

## 🚀 Quick Start

### 📦 Installation

**From crates.io (recommended):**
```bash
cargo install cctx
```

**From source:**
```bash
git clone https://github.com/nwiizo/cctx.git
cd cctx
cargo install --path .
```

**Pre-built binaries:**
Download from [GitHub Releases](https://github.com/nwiizo/cctx/releases)

### ⚡ 30-Second Setup

```bash
# 1. Create your first context from current settings
cctx -n personal

# 2. Create a restricted work context
cctx -n work

# 3. Switch between contexts
cctx work      # Switch to work
cctx personal  # Switch to personal  
cctx -         # Switch back to previous
```

## 🎯 Usage

### 🔍 Basic Commands

```bash
# List all contexts (current highlighted in green)
cctx

# Switch to a context
cctx work

# Switch to previous context  
cctx -

# Show current context
cctx -c
```

### 🏗️ Settings Level Management

cctx respects [Claude Code's settings hierarchy](https://docs.anthropic.com/en/docs/claude-code/settings) with a simple, predictable approach:

1. **Enterprise policies** (highest priority)
2. **Command-line arguments** 
3. **Local project settings** (`./.claude/settings.local.json`)
4. **Shared project settings** (`./.claude/settings.json`)
5. **User settings** (`~/.claude/settings.json`) (lowest priority)

```bash
# Default: always uses user-level contexts (predictable)
cctx                       # Manages ~/.claude/settings.json

# Explicit flags for project/local contexts
cctx --in-project          # Manages ./.claude/settings.json
cctx --local               # Manages ./.claude/settings.local.json

# All commands work with any level
cctx --in-project work     # Switch to 'work' in project contexts
cctx --local staging       # Switch to 'staging' in local contexts
```

### 🛠️ Context Management

```bash
# Create new context from current settings
cctx -n project-alpha

# Delete a context
cctx -d old-project

# Rename a context
cctx -r old-name new-name

# Edit context with $EDITOR
cctx -e work

# Show context content (JSON)
cctx -s production

# Unset current context
cctx -u
```

### 📥📤 Import/Export

```bash
# Export context to file
cctx --export production > prod-settings.json

# Import context from file
cctx --import staging < staging-settings.json

# Share contexts between machines
cctx --export work | ssh remote-host 'cctx --import work'
```

### 🔀 Merge Permissions

Merge permissions from other contexts or files to build complex configurations:

```bash
# Merge user settings into current context
cctx --merge-from user

# Merge from another context
cctx --merge-from personal work

# Merge from a specific file
cctx --merge-from /path/to/permissions.json staging

# Remove previously merged permissions
cctx --unmerge user

# View merge history
cctx --merge-history

# Merge into a specific context (default is current)
cctx --merge-from user production
```

**Merge Features:**
- 📋 **Smart deduplication** - Prevents duplicate permissions
- 📝 **History tracking** - See what was merged from where
- 🔄 **Reversible** - Unmerge specific sources anytime
- 🎯 **Granular control** - Target specific contexts

### 🖥️ Shell Completions

Enable tab completion for faster workflow:

```bash
# Bash
cctx --completions bash > ~/.local/share/bash-completion/completions/cctx

# Zsh  
cctx --completions zsh > /usr/local/share/zsh/site-functions/_cctx

# Fish
cctx --completions fish > ~/.config/fish/completions/cctx.fish

# PowerShell
cctx --completions powershell > cctx.ps1
```

## 🏗️ File Structure

Contexts are stored as individual JSON files at different levels:

**🏠 User Level (`~/.claude/`):**
```
📁 ~/.claude/
├── ⚙️ settings.json           # Active user context
└── 📁 settings/
    ├── 💼 work.json          # Work context  
    ├── 🏠 personal.json      # Personal context
    └── 🔒 .cctx-state.json   # State tracking
```

**📁 Project Level (`./.claude/`):**
```
📁 ./.claude/
├── ⚙️ settings.json           # Shared project context
├── 🔒 settings.local.json     # Local project context (gitignored)
└── 📁 settings/
    ├── 🚀 staging.json       # Staging context
    ├── 🏭 production.json    # Production context
    ├── 🔒 .cctx-state.json   # Project state
    └── 🔒 .cctx-state.local.json # Local state
```

## 🎭 Interactive Mode

When no arguments are provided, cctx enters interactive mode:

- 🔍 **fzf integration** - Uses fzf if available for fuzzy search
- 🎯 **Built-in finder** - Fallback fuzzy finder when fzf not installed
- 🌈 **Color coding** - Current context highlighted in green
- ⌨️ **Keyboard navigation** - Arrow keys and type-ahead search

```bash
# Interactive context selection
cctx
```

## 💼 Common Workflows

### 🏢 Professional Setup

```bash
# Create restricted work context for safer collaboration
cctx -n work
cctx -e work  # Edit to add restrictions:
# - Read/Edit only in ~/work/** and current directory
# - Deny: docker, kubectl, terraform, ssh, WebFetch, WebSearch
# - Basic dev tools: git, npm, cargo, python only
```

### 🚀 Project-Based Contexts

```bash
# Create project-specific contexts
cctx -n client-alpha    # For client work
cctx -n side-project    # For personal projects  
cctx -n experiments     # For trying new things

# Switch based on current work
cctx client-alpha       # Restricted permissions
cctx experiments        # Full permissions for exploration
```

### 🔄 Daily Context Switching

```bash
# Morning: start with work context
cctx work

# Need full access for personal project  
cctx personal

# Quick switch back to work
cctx -

# Check current context anytime
cctx -c
```

### 🛡️ Security-First Approach

```bash
# Default restricted context for screen sharing
cctx work

# Full permissions only when needed
cctx personal

# Project-specific minimal permissions
cctx -n client-project
# Configure: only access to ~/projects/client/** 
```

### 🎯 Settings Level Workflows

**👤 User-Level Development:**
```bash
# Personal development with full permissions (default behavior)
cctx personal

# Work context with restrictions (default behavior)
cctx work
```

**📁 Project-Level Collaboration:**
```bash
# Shared team settings (committed to git)
cctx --in-project staging
cctx --in-project production

# Personal project overrides (gitignored)
cctx --local development
cctx --local debug
```

**🔄 Multi-Level Management:**
```bash
# Check current level (always shows helpful context)
cctx                    # Shows: 👤 User contexts + hints for project/local if available

# Switch levels in same directory
cctx personal           # User level (default)
cctx --in-project staging  # Project level  
cctx --local debug      # Local level
```

## 🔧 Advanced Usage

### 📝 Context Creation with Claude

Use Claude Code to help create specialized contexts:

```bash
# Create production-safe context
claude --model opus <<'EOF'
Create a production.json context file with these restrictions:
- Read-only access to most files
- No docker/kubectl/terraform access  
- No system file editing
- Limited bash commands for safety
- Based on my current ~/.claude/settings.json but secured
EOF
```

### 🎨 Custom Context Templates

```bash
# Create template contexts for different scenarios
cctx -n template-minimal     # Minimal permissions
cctx -n template-dev         # Development tools only
cctx -n template-ops         # Operations/deployment tools
cctx -n template-restricted  # Screen-sharing safe
```

### 🔄 Context Synchronization

```bash
# Sync contexts across machines
rsync -av ~/.claude/settings/ remote:~/.claude/settings/

# Or use git for version control
cd ~/.claude/settings
git init && git add . && git commit -m "Initial contexts"
git remote add origin git@github.com:user/claude-contexts.git
git push -u origin main
```

## 🛡️ Security Best Practices

### 🔒 Permission Isolation

1. **🏢 Work context** - Restricted permissions for professional use
2. **🏠 Personal context** - Full permissions for personal projects
3. **📺 Demo context** - Ultra-restricted for screen sharing/demos
4. **🧪 Testing context** - Isolated environment for experiments

### 🎯 Context Strategy

```bash
# Create permission hierarchy
cctx -n restricted   # No file write, no network, no system access
cctx -n development  # File access to ~/dev/**, basic tools only  
cctx -n full        # All permissions for personal use
cctx -n demo        # Read-only, safe for presentations
```

### 🔍 Regular Audits

```bash
# Review context permissions regularly
cctx -s work        # Check work context permissions
cctx -s personal    # Review personal context
cctx -s production  # Audit production context

# Quick security check
cctx -s restricted | grep -i "allow\|deny"
```

## 🎯 Tips & Tricks

### ⚡ Productivity Boosters

- 🔄 **Use `cctx -` frequently** - Quick toggle between two contexts
- 🎯 **Trust the defaults** - `cctx` (no flags) handles 90% of use cases perfectly
- 💡 **Follow the hints** - When cctx shows hints, they're contextually relevant
- ⌨️ **Set up aliases** - `alias work='cctx work'`, `alias home='cctx personal'`
- 📝 **Document your contexts** - Add comments in JSON for future reference

### 🛠️ Environment Setup

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc)
export EDITOR=code                    # For cctx -e
alias cx='cctx'                      # Shorter command
alias cxs='cctx -s'                  # Show context content
alias cxc='cctx -c'                  # Show current context

# Git hooks for automatic context switching
# Pre-commit hook to ensure proper context
#!/bin/bash
if [[ $(cctx -c) != "work" ]]; then
  echo "⚠️  Switching to work context for this repo"
  cctx work
fi
```

### 🔧 Integration Examples

```bash
# Tmux integration - show context in status bar
set -g status-right "Context: #(cctx -c) | %H:%M"

# VS Code integration - add to settings.json
"terminal.integrated.env.osx": {
  "CLAUDE_CONTEXT": "$(cctx -c 2>/dev/null || echo 'none')"
}

# Fish shell prompt integration
function fish_prompt
    set_color cyan
    echo -n (cctx -c 2>/dev/null || echo 'no-context')
    set_color normal
    echo -n '> '
end
```

## 🔧 Development & Release Tools

This project includes comprehensive automation tools:

### 🚀 Release Management

**Simple One-Command Release:**
```bash
# Automatic release with all quality checks
./quick-release.sh patch      # 0.1.0 -> 0.1.1
./quick-release.sh minor      # 0.1.0 -> 0.2.0
./quick-release.sh major      # 0.1.0 -> 1.0.0
```

The script automatically:
- ✅ Runs quality checks (fmt, clippy, test, build)
- ✅ Updates version in Cargo.toml
- ✅ Creates git commit and tag
- ✅ Pushes to GitHub
- ✅ Triggers GitHub Actions for binary builds and crates.io publishing

### 🛠️ Development Tasks

```bash
# Using justfile (install: cargo install just)
just check              # Run all quality checks
just release-patch      # Same as ./quick-release.sh patch
just setup              # Setup development environment
just audit              # Security audit
just completions fish   # Generate shell completions
```

## 🤝 Contributing

We welcome contributions! This project includes:

- 🔄 **Automated CI/CD** - GitHub Actions for testing and releases
- 🧪 **Quality gates** - Formatting, linting, and tests required
- 📦 **Multi-platform** - Builds for Linux, macOS, and Windows
- 🚀 **Auto-releases** - Semantic versioning with automated publishing

### 🔑 Setting up crates.io Publishing (Maintainers)

To enable automatic publishing to crates.io:

1. **Get your crates.io API token:**
   ```bash
   cargo login  # Opens browser to get token
   # Or visit https://crates.io/me → New Token
   ```

2. **Add to GitHub repository secrets:**
   
   **Web UI method:**
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CARGO_REGISTRY_TOKEN`
   - Value: Your crates.io API token
   
   **CLI method (using gh):**
   ```bash
   # Store token securely and add to repository
   echo "YOUR_TOKEN" | gh secret set CARGO_REGISTRY_TOKEN
   ```

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📖 Complete Command Reference

### Basic Operations
- `cctx` - List contexts (defaults to user-level)
- `cctx <name>` - Switch to context
- `cctx -` - Switch to previous context
- `cctx -c` - Show current context name
- `cctx -q` - Quiet mode (only show current context)

### Context Management
- `cctx -n <name>` - Create new context from current settings
- `cctx -d <name>` - Delete context (interactive if no name)
- `cctx -r <old> <new>` - Rename context
- `cctx -e [name]` - Edit context with $EDITOR
- `cctx -s [name]` - Show context content (JSON)
- `cctx -u` - Unset current context (removes settings file)

### Import/Export
- `cctx --export [name]` - Export context to stdout
- `cctx --import <name>` - Import context from stdin

### Merge Operations
- `cctx --merge-from <source> [target]` - Merge permissions from source into target (default: current)
  - Source can be: `user`, another context name, or file path
- `cctx --merge-from <source> --merge-full [target]` - Merge ALL settings (not just permissions)
- `cctx --unmerge <source> [target]` - Remove previously merged permissions
- `cctx --unmerge <source> --merge-full [target]` - Remove ALL previously merged settings
- `cctx --merge-history [name]` - Show merge history for context

### Settings Levels
- `cctx` - User-level contexts (default: `~/.claude/settings.json`)
- `cctx --in-project` - Project-level contexts (`./.claude/settings.json`)
- `cctx --local` - Local project contexts (`./.claude/settings.local.json`)

### Other Options
- `cctx --completions <shell>` - Generate shell completions
- `cctx --help` - Show help information
- `cctx --version` - Show version information

## 🎯 Design Philosophy (v0.1.1+)

**cctx follows the principle of "Predictable defaults with explicit overrides":**

- 🎯 **Default behavior is always the same** - uses user-level contexts (`~/.claude/settings.json`)
- 💡 **Helpful discovery** - shows hints when project/local contexts are available
- 🚀 **Simple when simple** - 90% of usage needs zero flags
- 🔧 **Explicit when needed** - `--in-project` and `--local` for specific cases

This approach eliminates surprises and cognitive overhead while maintaining full functionality.

## ⚠️ Compatibility Notice

**cctx** is designed to work with [Claude Code](https://github.com/anthropics/claude-code) configuration files. As Claude Code is actively developed by Anthropic, configuration formats and file structures may change over time.

**We are committed to maintaining compatibility:**
- 🔄 **Active monitoring** of Claude Code updates and changes
- 🚀 **Prompt updates** when configuration formats change
- 🛠️ **Backward compatibility** whenever possible
- 📢 **Clear migration guides** for breaking changes

If you encounter compatibility issues after a Claude Code update, please [open an issue](https://github.com/nwiizo/cctx/issues) and we'll address it promptly.

## 🙏 Acknowledgments

- 🎯 Inspired by [kubectx](https://github.com/ahmetb/kubectx) - the amazing Kubernetes context switcher
- 🤖 Built for [Claude Code](https://claude.ai/code) - Anthropic's CLI for Claude
- 🦀 Powered by [Rust](https://www.rust-lang.org/) - fast, safe, and beautiful

---

<div align="center">

**⭐ Star this repo if cctx makes your Claude Code workflow better!**

[🐛 Report Bug](https://github.com/nwiizo/cctx/issues) • [💡 Request Feature](https://github.com/nwiizo/cctx/issues) • [💬 Discussions](https://github.com/nwiizo/cctx/discussions)

</div>
````
