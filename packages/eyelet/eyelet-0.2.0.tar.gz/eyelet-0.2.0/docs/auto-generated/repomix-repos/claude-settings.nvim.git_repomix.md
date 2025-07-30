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
README.md
task.md
```

# Files

## File: README.md
````markdown
# claude-settings.nvim

A Neovim plugin for quickly creating and managing Claude Code's `settings.json` configuration files.

## Features

- 🚀 Quick creation of `.claude/settings.json` files
- 📋 Multiple predefined permission templates
- 🎨 Interactive configuration wizard
- ✅ Configuration validation
- 💾 Automatic backup of existing configurations
- 🔧 Support for custom templates
- 🌍 Project-level and global configuration support

## Installation

### Using [vim-plug](https://github.com/junegunn/vim-plug)

```vim
" In your ~/.vimrc or ~/.config/nvim/init.vim
call plug#begin()
  " ... other plugins
  Plug 'pittcat/claude-settings.nvim'
call plug#end()

" Initialize the plugin
lua require('claude-settings').setup()
```

After adding the plugin, run `:PlugInstall` to install it.

### Using [lazy.nvim](https://github.com/folke/lazy.nvim)

```lua
{
  "pittcat/claude-settings.nvim",
  config = function()
    require("claude-settings").setup()
  end
}
```

### Using [packer.nvim](https://github.com/wbthomason/packer.nvim)

```lua
use {
  'pittcat/claude-settings.nvim',
  config = function()
    require('claude-settings').setup()
  end
}
```

## Quick Start

### Basic Commands

```vim
" Create project-level settings
:ClaudeSettingsInit

" Create global settings
:ClaudeSettingsInit global

" Select from templates
:ClaudeSettingsTemplate

" Edit existing settings
:ClaudeSettingsEdit

" Validate settings
:ClaudeSettingsValidate
```

### Default Key Mappings

- `<leader>cs` - Initialize Claude settings
- `<leader>ct` - Select template
- `<leader>ce` - Edit settings
- `<leader>cv` - Validate settings

## Configuration

```lua
require('claude-settings').setup({
  -- Auto backup existing configuration files
  auto_backup = true,
  
  -- Default template to use
  default_template = "basic",
  
  -- Open file after creation
  auto_open_after_create = false,
  
  -- Key mappings
  mappings = {
    init = "<leader>cs",
    template = "<leader>ct",
    edit = "<leader>ce",
    validate = "<leader>cv"
  },
  
  -- Validation settings
  validation = {
    validate_on_save = true,
    strict_mode = false
  }
})
```

## Built-in Templates

### Basic
Basic development permissions for general coding:
- Read all files
- Edit source files
- Git commands

### Development
Full development permissions:
- NPM/build commands
- Full file editing capabilities
- Search and grep functionality

### Secure
Restricted permissions for sensitive projects:
- Read/edit source files only
- No shell command execution
- No web access

### Testing
Optimized for test development:
- Test file access
- Test command execution
- Source file reading

### Documentation
For documentation work:
- Edit markdown files
- Read all files
- No code execution

### Minimal
Read-only access:
- File reading
- Search capabilities
- No modifications allowed

## Custom Templates

Create custom templates by saving JSON files to:
```
~/.local/share/nvim/claude-settings/templates/
```

Example custom template (`mytemplate.json`):
```json
{
  "permissions": {
    "allow": [
      "Read(**/*.ts)",
      "Edit(src/**/*.ts)",
      "Bash(npm run build)"
    ],
    "deny": [
      "Bash(rm *)",
      "WebFetch(*)"
    ]
  }
}
```

## Interactive Configuration

The plugin provides an interactive wizard for creating custom configurations:

1. Select allowed permissions from a list
2. Add custom permission patterns
3. Configure deny rules for security
4. Preview and save your configuration

## API

```lua
-- Initialize settings
require('claude-settings').init_settings('project')

-- Select template programmatically
require('claude-settings').select_template()

-- Validate configuration
require('claude-settings').validate_settings('project')
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
````

## File: task.md
````markdown
# Claude Settings Vim插件开发计划书

## 📋 项目概述

**项目名称**: claude-settings.nvim  
**功能**: 在Vim/Neovim中快速创建和管理Claude Code的settings.json配置文件  
**实现语言**: Lua (Neovim) + VimScript兼容  
**目标用户**: 使用Claude Code的开发者

## 🎯 核心功能需求

### 1. 基础功能
- [x] 创建 `.claude/settings.json` 文件
- [x] 支持项目级和全局级配置
- [x] 预设权限模板选择
- [x] 智能目录检测和创建

### 2. 高级功能
- [x] 交互式权限配置界面
- [x] 模板管理和自定义
- [x] 配置验证和语法检查
- [x] 备份现有配置

## 🏗️ 技术架构

### 文件结构
```
plugin/
├── claude-settings.lua          # 主插件文件
├── lua/
│   └── claude-settings/
│       ├── init.lua            # 插件入口
│       ├── config.lua          # 配置管理
│       ├── templates.lua       # 模板定义
│       ├── ui.lua             # 用户界面
│       └── utils.lua          # 工具函数
└── doc/
    └── claude-settings.txt     # 文档
```

### 核心模块设计

#### 1. 配置模板系统 (`templates.lua`)
```lua
local templates = {
  basic = {
    permissions = {
      allow = {"Read(*)", "Edit(src/**)", "Bash(git *)"},
      deny = {"Bash(rm -rf *)", "Bash(curl *)"}
    }
  },
  full_development = {
    permissions = {
      allow = {
        "Bash(npm run *)", "Bash(git *)", 
        "Edit(src/**)", "Edit(docs/**)",
        "Read(*)", "Glob(*)", "Grep(*)"
      },
      deny = {"Bash(rm -rf *)", "Bash(curl *)"}
    }
  },
  secure = {
    permissions = {
      allow = {"Read(src/**)", "Edit(src/**/*.js)"},
      deny = {"Bash(*)", "Edit(.*)", "WebFetch(*)"}
    }
  }
}
```

#### 2. UI交互系统 (`ui.lua`)
- 使用 `vim.ui.select` 进行模板选择
- `vim.ui.input` 进行自定义配置
- telescope.nvim 集成（可选）

#### 3. 工具函数 (`utils.lua`)
- 文件操作：创建目录、写入JSON
- 路径检测：项目根目录、.claude目录
- JSON处理：格式化、验证

## 🔧 实现细节

### Phase 1: 基础功能实现

#### 1.1 主命令定义
```lua
-- 主要用户命令
vim.api.nvim_create_user_command('ClaudeSettingsInit', function(opts)
  require('claude-settings').init_settings(opts.args)
end, {
  nargs = '?',
  complete = function() return {'project', 'global'} end,
  desc = 'Initialize Claude settings'
})

vim.api.nvim_create_user_command('ClaudeSettingsTemplate', function()
  require('claude-settings').select_template()
end, { desc = 'Select Claude settings template' })
```

#### 1.2 核心逻辑流程
1. **检测环境**
   - 确定是项目级还是全局级配置
   - 检查现有配置文件
   - 创建必要的目录结构

2. **模板选择**
   - 显示可用模板列表
   - 允许用户预览模板内容
   - 支持自定义模板

3. **配置生成**
   - 合并用户选择的配置
   - 生成格式化的JSON
   - 写入指定位置

#### 1.3 关键函数实现

```lua
-- 检测项目根目录
local function find_project_root()
  local git_root = vim.fn.systemlist('git rev-parse --show-toplevel')[1]
  if vim.v.shell_error == 0 then
    return git_root
  end
  return vim.fn.getcwd()
end

-- 创建配置文件
local function create_settings_file(config, target_path)
  local claude_dir = target_path .. '/.claude'
  vim.fn.mkdir(claude_dir, 'p')
  
  local settings_path = claude_dir .. '/settings.json'
  local json_content = vim.fn.json_encode(config)
  
  -- 格式化JSON
  local formatted = format_json(json_content)
  
  -- 写入文件
  local file = io.open(settings_path, 'w')
  file:write(formatted)
  file:close()
  
  vim.notify('Claude settings created: ' .. settings_path)
end
```

### Phase 2: 高级功能实现

#### 2.1 交互式配置编辑器
```lua
local function interactive_config_editor()
  local config = {}
  
  -- 权限配置向导
  vim.ui.select({'Basic', 'Development', 'Secure', 'Custom'}, {
    prompt = 'Select permission level:'
  }, function(choice)
    if choice == 'Custom' then
      custom_permission_editor(config)
    else
      config = templates[choice:lower()]
      finalize_config(config)
    end
  end)
end
```

#### 2.2 配置验证系统
```lua
local function validate_config(config)
  local errors = {}
  
  -- 检查必需字段
  if not config.permissions then
    table.insert(errors, 'Missing permissions field')
  end
  
  -- 验证权限格式
  if config.permissions.allow then
    for _, perm in ipairs(config.permissions.allow) do
      if not validate_permission_pattern(perm) then
        table.insert(errors, 'Invalid permission pattern: ' .. perm)
      end
    end
  end
  
  return #errors == 0, errors
end
```

### Phase 3: 扩展功能

#### 3.1 模板管理系统
- 用户自定义模板存储
- 模板导入/导出功能
- 在线模板库集成

#### 3.2 配置同步功能
- 团队配置模板共享
- 版本控制集成
- 配置变更通知

## 🎨 用户界面设计

### 命令界面
```vim
:ClaudeSettingsInit project    " 创建项目级配置
:ClaudeSettingsInit global     " 创建全局配置
:ClaudeSettingsTemplate        " 选择模板
:ClaudeSettingsEdit           " 编辑现有配置
:ClaudeSettingsValidate       " 验证配置
```

### 快捷键映射
```lua
vim.keymap.set('n', '<leader>cs', '<cmd>ClaudeSettingsInit<cr>', 
  { desc = 'Initialize Claude Settings' })
vim.keymap.set('n', '<leader>ct', '<cmd>ClaudeSettingsTemplate<cr>', 
  { desc = 'Select Claude Template' })
```

### UI Flow
1. **启动命令** → 检测环境
2. **模板选择** → 显示选项列表
3. **权限配置** → 交互式编辑器
4. **预览确认** → 显示最终配置
5. **文件创建** → 写入并确认

## 🧪 测试计划

### 单元测试
- 模板系统测试
- 文件操作测试
- 配置验证测试

### 集成测试
- 不同项目结构下的测试
- 权限模式组合测试
- 错误处理测试

### 用户测试
- 新手友好性测试
- 工作流程效率测试
- 文档完整性验证

## 📚 文档计划

### 用户文档
- 安装指南
- 快速开始教程
- 命令参考
- 配置示例

### 开发者文档
- API参考
- 扩展指南
- 贡献指南

## 🚀 发布计划

### v1.0.0 (基础版本)
- ✅ 基础配置文件创建
- ✅ 3个预设模板
- ✅ 项目/全局模式支持

### v1.1.0 (增强版本)
- ✅ 交互式配置编辑器
- ✅ 配置验证功能
- ✅ 更多模板选项

### v1.2.0 (完整版本)
- ✅ 自定义模板系统
- ✅ 团队配置共享
- ✅ telescope.nvim 集成

## ⚠️ 风险和注意事项

1. **兼容性**: 确保Vim和Neovim的兼容性
2. **权限安全**: 避免生成不安全的权限配置
3. **文件覆盖**: 现有配置文件的备份策略
4. **依赖管理**: 最小化外部依赖

## 🎯 成功指标

- 配置文件创建成功率 > 99%
- 用户操作步骤 < 3步
- 插件启动时间 < 100ms
- 社区采用率目标：100+ stars
````
