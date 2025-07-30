# Hook Patterns Analysis

Generated: 2025-07-28

## Real-World Hook Examples Found

### 1. tenxhq/tenx-hooks - Rust PreToolUse Hook

**Source**: https://github.com/tenxhq/tenx-hooks  
**Language**: Rust  
**Hook Type**: PreToolUse  
**Purpose**: Safety check for dangerous bash commands

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

**Key Patterns Identified:**

1. **Input Reading**: `PreToolUse::read()` - standard input reading pattern
2. **Tool Filtering**: `input.tool_name == "Bash"` - target specific tools
3. **Parameter Access**: `input.tool_input.get("command")` - access tool parameters
4. **Response Types**: 
   - `input.block("message")` - block execution with message
   - `input.approve("message")` - allow execution with message
5. **Error Handling**: Uses `Result<()>` return type

### 2. Claude Code Official Examples

**Source**: claude-code repository (`examples/hooks/bash_command_validator_example.py`)  
**Language**: Python  
**Hook Type**: PreToolUse  
**Purpose**: Command validation and user interaction

**Key Patterns:**
1. **Exit Codes**:
   - `exit(1)` - Show message to user only
   - `exit(2)` - Block execution and show message to Claude
   - `exit(0)` - Allow execution
2. **Input Format**: JSON via stdin
3. **Environment Variables**: Access to context

## Pattern Classification

### A. Safety/Security Hooks
- **Purpose**: Prevent dangerous commands
- **Pattern**: Check command content → block if dangerous
- **Examples**: 
  - Prevent `rm -rf /`
  - Block `sudo` commands
  - Validate file paths

### B. Logging/Monitoring Hooks
- **Purpose**: Track tool usage and results
- **Pattern**: Log input → allow execution → log output
- **Examples**:
  - Command history logging
  - Performance monitoring
  - Usage analytics

### C. Enhancement Hooks
- **Purpose**: Improve or modify tool behavior
- **Pattern**: Modify input → allow execution → enhance output
- **Examples**:
  - Add context to prompts
  - Format outputs
  - Add metadata

### D. Workflow Hooks
- **Purpose**: Coordinate between tools
- **Pattern**: Check state → decide action → update state
- **Examples**:
  - Multi-step workflows
  - State machine management
  - Dependency tracking

## Implementation Strategies

### 1. Language-Specific Approaches

#### Rust (tenx-hooks model)
- **Pros**: Type safety, performance, rich ecosystem
- **Cons**: Compilation required, complexity
- **Best for**: High-performance, safety-critical hooks

#### Python (official examples)
- **Pros**: Rapid development, rich libraries, no compilation
- **Cons**: Runtime overhead, dependency management
- **Best for**: Quick prototypes, data processing, integrations

#### Shell Scripts
- **Pros**: Universal availability, simple deployment
- **Cons**: Limited functionality, error-prone
- **Best for**: Simple checks, system integration

### 2. Common Input/Output Patterns

#### Input Processing
```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "ls -la",
    "description": "List files in current directory"
  },
  "context": {
    "working_directory": "/path/to/project",
    "user": "username"
  }
}
```

#### Response Patterns
- **Allow**: Exit code 0, no output
- **Block with user message**: Exit code 1, message to stderr
- **Block with Claude message**: Exit code 2, message to stderr
- **Modify**: Exit code 0, modified JSON to stdout

### 3. Template Patterns

#### Basic Safety Check Template
```python
#!/usr/bin/env python3
import json
import sys

def main():
    try:
        input_data = json.load(sys.stdin)
        
        # Extract tool info
        tool_name = input_data.get("tool_name")
        tool_input = input_data.get("tool_input", {})
        
        # Your safety logic here
        if is_dangerous(tool_name, tool_input):
            print("Command blocked for safety", file=sys.stderr)
            sys.exit(2)  # Block and show to Claude
            
        # Allow execution
        sys.exit(0)
        
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Fail open for safety

def is_dangerous(tool_name, tool_input):
    # Your danger detection logic
    pass

if __name__ == "__main__":
    main()
```

## Recommendations for Rigging

### 1. Template Library
Create templates for common patterns:
- `safety-check` - Basic command validation
- `logger` - Comprehensive logging
- `enhancer` - Output modification
- `workflow` - Multi-step coordination

### 2. Pattern Detection
Automatically suggest hook types based on:
- Tool usage patterns
- Project structure
- User preferences
- Common vulnerabilities

### 3. Testing Framework
Integrate with hook testing:
- Unit tests for hook logic
- Integration tests with Claude Code
- Performance benchmarking
- Safety validation

### 4. Configuration Management
Support multiple configuration strategies:
- Per-project hooks
- Global user hooks
- Team/organization hooks
- Conditional activation

## Next Steps

1. **Expand Pattern Library**: Search more repositories for diverse examples
2. **Create Template Generator**: Automate hook creation from patterns
3. **Build Testing Suite**: Validate hooks before deployment
4. **Documentation**: Create comprehensive hook development guides