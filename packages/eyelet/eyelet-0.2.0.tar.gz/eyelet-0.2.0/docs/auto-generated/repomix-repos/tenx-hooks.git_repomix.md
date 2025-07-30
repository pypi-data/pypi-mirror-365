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
## Project Overview

## Model guidance

- Prefer to write durable integration tests over running commands/examples or
  creating disposable test scripts.
- This is a free-standing tool, so don't create examples in an `examples/` directory.
- Running fmt and clippy is a requirement before submitting code.


## Development Commands

### Building and Testing
```bash
# Build the project
cargo build

# Run all tests including workspace tests
cargo test --workspace

# Run tests with output (useful for debugging)
cargo test -- --nocapture

# Run a specific test
cargo test test_name

# Check code without building
cargo check

# Run linter
cargo clippy --examples --tests

# Format code - ALWAYS DO THIS BEFORE SUBMITTING CODE
cargo fmt --all

# Run linter with automatic fixes - ALWAYS DO THIS BEFORE SUBMITTING CODE
cargo clippy --fix --allow-dirty --examples --tests
```
````

## File: README.md
````markdown
# Code Hooks

Rust toolkit for building hooks for [Claude Code](https://claude.ai/code).
Hooks are shell commands that execute at various points in Claude Code's
lifecycle.

## Crates

- **[code-hooks](./crates/code-hooks/)**: Core library for building Claude Code
  hooks
- **[claude-transcript](./crates/claude-transcript/)**: Parse and analyze
  Claude conversation transcripts  
- **[hooktest](./crates/hooktest/)**: Test hooks during development
- **[rust-hook](./crates/rust-hook/)**: Example hook that formats and lints
  Rust code

## Quick Start

```rust
use code_hooks::*;

fn main() -> Result<()> {
    let input = PreToolUse::read()?;
    
    if input.tool_name == "Bash" {
        if let Some(cmd) = input.tool_input.get("command").and_then(|v| v.as_str()) {
            if cmd.contains("rm -rf /") {
                return input.block("Dangerous command").respond();
            }
        }
    }
    
    input.approve("OK").respond()
}
```

Test with hooktest:
```bash
hooktest pretool --tool Bash --tool-input command="ls" -- ./my-hook
```
````
