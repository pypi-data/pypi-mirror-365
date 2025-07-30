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
settings.json
```

# Files

## File: CLAUDE.md
````markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository contains comprehensive permission settings for Claude Code. The main file is `settings.json` which defines allowed and denied operations for Claude Code sessions.

## Key Architecture

### Settings Structure
The `settings.json` file contains a single root object with a `permissions` key that has two arrays:
- `allow`: Patterns for permitted operations (1000+ patterns)
- `deny`: Patterns for blocked operations (security-focused)

Pattern format: `"Tool(specifier)"` where Tool is the Claude tool name (Bash, Read, WebFetch, etc.) and specifier is the pattern to match.

### Settings Hierarchy
Claude Code applies settings in order of precedence:
1. Enterprise policies: `/Library/Application Support/ClaudeCode/policies.json` (macOS)
2. Command line arguments
3. Local project settings: `.claude/settings.local.json`
4. Shared project settings: `.claude/settings.json`
5. User/Global settings: `~/.claude/settings.json`

## Common Development Tasks

### Validating JSON Syntax
```bash
# Check if settings.json is valid JSON
python -m json.tool settings.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"

# Pretty-print and validate
python -m json.tool settings.json > settings.formatted.json
```

### Testing Permission Patterns
When adding new patterns, ensure they follow the correct format:
- Bash commands: `"Bash(command pattern)"`
- File operations: `"Read(**)"`, `"Edit(**)"`, `"Write(**)"` 
- Web operations: `"WebFetch(domain:example.com)"`

### Deploying Settings
```bash
# Deploy as system-wide policy (macOS, requires sudo)
sudo ln -sf /path/to/settings.json "/Library/Application Support/ClaudeCode/policies.json"

# Deploy as user global settings
mkdir -p ~/.claude
cp settings.json ~/.claude/settings.json

# Deploy as project settings
mkdir -p .claude
cp settings.json .claude/settings.json
```

## Important Considerations

1. **Personal Settings**: Keep personal server names and domains in separate files (`.claude/settings.local.json` or `~/.claude/settings.json`), not in the main `settings.json` which is for community use.

2. **Security**: The deny list is critical for preventing malicious operations. Always test new patterns carefully and consider security implications.

3. **Pattern Specificity**: More specific patterns take precedence. For example, `"Bash(rm -rf /)"` in deny will override `"Bash(rm *)"` in allow.

4. **Merging Behavior**: Settings files merge additively - patterns from multiple files combine rather than replace each other.
````

## File: README.md
````markdown
# Claude Code Settings

This repository contains comprehensive permission settings for Claude Code, Anthropic's AI-powered coding assistant.

## Settings Hierarchy and Precedence

According to the [official Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/settings), settings are applied in the following order of precedence (from highest to lowest):

1. **Enterprise policies**
   - macOS: `/Library/Application Support/ClaudeCode/policies.json`
   - Linux/Windows WSL: `/etc/claude-code/policies.json`
   - These are system-wide policies that cannot be overridden

2. **Command line arguments**
   - Flags passed when running Claude Code
   - Example: `claude --allow "Bash(npm test)"`

3. **Local project settings** 
   - Location: `.claude/settings.local.json`
   - Project-specific overrides for individual developers
   - Should be added to `.gitignore`

4. **Shared project settings**
   - Location: `.claude/settings.json` 
   - Team/project settings checked into version control
   - This is what this repository provides

5. **User/Global settings**
   - Location: `~/.claude/settings.json`
   - Personal preferences across all projects
   - Lowest precedence

## How Settings Merge

Settings files are merged together, with higher precedence files overriding values from lower precedence files. This allows:

- Users to set personal defaults globally
- Teams to share common project settings
- Individual developers to override both for their local environment
- Enterprises to enforce security policies

## Available Settings Files

This repository provides two versions of the settings file:

1. **settings.json** - Clean configuration without comments, ideal for direct use
2. **settings.jsonc** - Same configuration with detailed comments explaining each section

The JSONC version is helpful when you want to understand and customize the settings, while the regular JSON version is cleaner for production use.

## Using These Settings

### Option 1: As Team/Project Settings
Copy `settings.json` (or `settings.jsonc` if you prefer the commented version) to your project's `.claude/settings.json`:

```bash
mkdir -p .claude
# For clean version without comments
curl -o .claude/settings.json https://raw.githubusercontent.com/dwillitzer/claude-settings/main/settings.json

# OR for commented version
curl -o .claude/settings.json https://raw.githubusercontent.com/dwillitzer/claude-settings/main/settings.jsonc
```

### Option 2: As Global User Settings
Copy to your home directory:

```bash
mkdir -p ~/.claude
# For clean version without comments
curl -o ~/.claude/settings.json https://raw.githubusercontent.com/dwillitzer/claude-settings/main/settings.json

# OR for commented version
curl -o ~/.claude/settings.json https://raw.githubusercontent.com/dwillitzer/claude-settings/main/settings.jsonc
```

### Option 3: As Local Overrides
For project-specific overrides, create `.claude/settings.local.json` and add to `.gitignore`:

```bash
echo ".claude/settings.local.json" >> .gitignore
```

## Permissions Overview

This configuration includes:

### Allow List (900+ patterns)
- **Docker & Container Orchestration**: Docker (containers, compose, volumes, networks), Kubernetes (kubectl, helm), Podman
- **Git & GitHub**: All git operations, GitHub CLI (gh) for PRs, issues, repos, workflows
- **Programming Languages & Package Managers**: 
  - JavaScript/TypeScript: npm, yarn, pnpm, bun, deno
  - Python: pip, pipenv, poetry, pyenv
  - Rust: cargo, rustc, rustup
  - Go: go mod, go build, go test
  - Ruby: gem, bundle, rbenv
  - Java: maven, gradle, javac
  - PHP: composer, php
- **Cloud Provider CLIs**: AWS CLI, Google Cloud SDK, Azure CLI, Vercel, Netlify, Heroku
- **Database Tools**: PostgreSQL, MySQL, MongoDB, SQLite, Redis with full client support
- **Development Environment**: Version managers (nvm, pyenv, rbenv), tmux, screen, direnv
- **File & Text Processing**: Read/write/edit files, grep, sed, awk, jq, yq, pipe operations
- **System Package Management**: apt, yum, dnf, brew, snap (with controlled sudo access)
- **Web & API Tools**: curl (all methods), wget, API testing, http-server
- **SSH/Remote Access**: SSH connections, SCP, rsync to specified servers
- **System Utilities**: Process management, network tools, system monitoring
- **Data Processing**: tar, zip, gzip, 7z, JSON/YAML processing
- **Claude-specific tools**: Read, Edit, MultiEdit, Glob, Grep, WebFetch, WebSearch, TodoRead, TodoWrite, Task

### Deny List (Security-focused)
- **Destructive operations**: Prevents rm -rf /, format commands, mass deletion
- **Security risks**: Blocks reverse shells, credential theft attempts, malicious downloads
- **System damage**: Prevents shutdown, reboot, firewall disabling, kernel modifications
- **Data exposure**: Blocks credential searches, cloud metadata access, password history
- **Malicious activities**: Prevents crypto mining, network backdoors, process injection
- **Dangerous Docker**: Blocks privileged containers, host PID/network access, socket mounting
- **User management**: Prevents password changes, user account modifications
- **Log deletion**: Blocks removal of system logs and audit trails

## Customization

To customize for your needs:

1. Fork this repository
2. Edit `settings.json` to add/remove permissions
3. Use the Tool(specifier) format:
   - `"Bash(git *)"` - Allow all git commands
   - `"Bash(rm -rf /)"` - Deny specific dangerous commands
   - `"Bash(* | grep *)"` - Allow pipe operations
   - `"Bash(kubectl get pods)"` - Allow specific Kubernetes commands
   - `"Read(**)"` - Allow reading any file
   - `"WebFetch(domain:*.example.com)"` - Allow fetching from specific domains

Common customizations:
- **Add new servers**: Update SSH patterns to include your servers
- **Add new tools**: Include patterns for additional development tools
- **Restrict further**: Add more patterns to the deny list
- **Domain access**: Add domains to WebFetch permissions as needed

## Security Considerations

- These settings are permissive for development productivity
- Review and adjust based on your security requirements
- Use enterprise policies for enforcing stricter controls
- Always use `settings.local.json` for sensitive project-specific settings
- Regularly audit the allow list to ensure it matches your needs
- Consider using more restrictive settings for production environments

### Sudo Permissions Warning

This configuration includes limited sudo access for package management only:
- `sudo apt install`, `sudo yum install`, etc. are allowed
- These are restricted to package installation commands
- **WARNING**: Review these permissions carefully for your environment
- Consider removing sudo permissions if not needed
- Never allow broad sudo access like `"Bash(sudo *)"` 

For maximum security, use a separate settings.local.json without sudo permissions for sensitive projects.

## Common Workflows

These permissions enable typical development workflows:

### Full-Stack Development
```bash
# Clone and setup a project
git clone https://github.com/user/project.git
cd project
npm install

# Run development servers
npm run dev
# or
docker-compose up -d

# Check logs
docker logs app-container | grep error
tail -f logs/app.log
```

### Working with GitHub
```bash
# Create a PR from Claude Code
gh pr create --title "Fix bug" --body "Description"

# Review PR status
gh pr status
gh pr checks

# Work with issues
gh issue list --label bug
gh issue create --title "New feature"
```

### Cloud Deployments
```bash
# Deploy to AWS
aws s3 sync ./build s3://my-bucket
aws cloudformation deploy --template-file template.yml

# Deploy to Vercel
vercel --prod

# Google Cloud operations
gcloud app deploy
gcloud compute instances list
```

### Database Operations
```bash
# PostgreSQL backup
pg_dump -h localhost -U user dbname > backup.sql

# MongoDB operations
mongosh --eval "db.collection.find()"
mongodump --db mydb --out ./backup

# Redis operations
redis-cli SET key value
redis-cli GET key
```

### Container Orchestration
```bash
# Kubernetes deployment
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs pod-name

# Helm charts
helm install myapp ./chart
helm upgrade myapp ./chart
```

## References

- [Claude Code Settings Documentation](https://docs.anthropic.com/en/docs/claude-code/settings) - Official settings hierarchy and configuration guide
- [Claude Code Security Documentation](https://docs.anthropic.com/en/docs/claude-code/security) - Security best practices and permission model
- [Claude Code CLI Usage](https://docs.anthropic.com/en/docs/claude-code/cli-usage) - Command line options and flags

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

Please ensure any new patterns follow the existing format and include both allow and deny considerations.

## License

MIT License - This configuration is provided as-is for the Claude Code community. Use at your own discretion.
````

## File: settings.json
````json
{
  "permissions": {
    "allow": [
      "Bash(docker ps)",
      "Bash(docker ps *)",
      "Bash(docker ps -a*)",
      "Bash(docker ps --format*)",
      "Bash(docker ps | grep*)",
      "Bash(docker ps -a | grep*)",
      
      "Bash(docker logs *)",
      "Bash(docker logs * --tail*)",
      "Bash(docker logs * --tail=*)",
      "Bash(docker logs * 2>&1*)",
      "Bash(docker logs * | grep*)",
      "Bash(docker logs * | tail*)",
      "Bash(docker logs * | head*)",
      
      "Bash(docker exec *)",
      "Bash(docker exec * printenv*)",
      "Bash(docker exec * cat *)",
      "Bash(docker exec * ls *)",
      "Bash(docker exec * rm *)",
      "Bash(docker exec * n8n *)",
      "Bash(docker exec * sh -c *)",
      "Bash(docker exec * bash -c *)",
      "Bash(docker exec * /bin/bash *)",
      "Bash(docker exec * /bin/sh *)",
      "Bash(docker exec * printenv | grep*)",
      
      "Bash(docker start *)",
      "Bash(docker stop *)",
      "Bash(docker restart *)",
      "Bash(docker rm *)",
      "Bash(docker rm -f *)",
      "Bash(docker kill *)",
      
      "Bash(docker inspect *)",
      "Bash(docker inspect * | jq*)",
      "Bash(docker inspect * | grep*)",
      
      "Bash(docker volume ls*)",
      "Bash(docker volume inspect *)",
      "Bash(docker volume rm *)",
      "Bash(docker volume create *)",
      "Bash(docker volume prune*)",
      
      "Bash(docker images*)",
      "Bash(docker pull *)",
      "Bash(docker build *)",
      "Bash(docker build --no-cache *)",
      "Bash(docker tag *)",
      "Bash(docker push *)",
      
      "Bash(docker compose *)",
      "Bash(docker compose up*)",
      "Bash(docker compose up -d*)",
      "Bash(docker compose down*)",
      "Bash(docker compose ps*)",
      "Bash(docker compose logs*)",
      "Bash(docker compose restart*)",
      "Bash(docker compose stop*)",
      "Bash(docker compose start*)",
      "Bash(docker compose build*)",
      "Bash(docker compose pull*)",
      "Bash(docker compose exec*)",
      "Bash(docker compose rm*)",
      "Bash(docker compose up -d --force-recreate*)",
      "Bash(docker compose build --no-cache*)",
      "Bash(docker-compose *)",
      
      "Bash(docker system *)",
      "Bash(docker info*)",
      "Bash(docker version*)",
      
      "Bash(kubectl *)",
      "Bash(kubectl get *)",
      "Bash(kubectl describe *)",
      "Bash(kubectl create *)",
      "Bash(kubectl apply *)",
      "Bash(kubectl delete *)",
      "Bash(kubectl exec *)",
      "Bash(kubectl logs *)",
      "Bash(kubectl port-forward *)",
      "Bash(kubectl cp *)",
      "Bash(kubectl scale *)",
      "Bash(kubectl rollout *)",
      "Bash(kubectl set *)",
      "Bash(kubectl edit *)",
      "Bash(kubectl patch *)",
      "Bash(kubectl label *)",
      "Bash(kubectl annotate *)",
      "Bash(kubectl expose *)",
      "Bash(kubectl run *)",
      "Bash(kubectl proxy*)",
      "Bash(kubectl config *)",
      "Bash(kubectl cluster-info*)",
      "Bash(kubectl top *)",
      "Bash(kubectl api-resources*)",
      "Bash(kubectl explain *)",
      "Bash(kubectl auth *)",
      "Bash(kubectl version*)",
      
      "Bash(helm *)",
      "Bash(helm install *)",
      "Bash(helm upgrade *)",
      "Bash(helm list*)",
      "Bash(helm repo *)",
      "Bash(helm search *)",
      "Bash(helm show *)",
      "Bash(helm pull *)",
      "Bash(helm delete *)",
      "Bash(helm rollback *)",
      "Bash(helm status *)",
      "Bash(helm test *)",
      "Bash(helm template *)",
      "Bash(helm dependency *)",
      "Bash(helm package *)",
      "Bash(helm lint *)",
      "Bash(helm create *)",
      
      "Bash(minikube *)",
      "Bash(minikube start*)",
      "Bash(minikube stop*)",
      "Bash(minikube status*)",
      "Bash(minikube dashboard*)",
      "Bash(minikube service *)",
      "Bash(minikube tunnel*)",
      
      "Bash(kind *)",
      "Bash(kind create cluster*)",
      "Bash(kind delete cluster*)",
      "Bash(kind get clusters*)",
      "Bash(kind load docker-image *)",
      
      "Bash(ssh gmktec-k9 *)",
      "Bash(ssh root@gmktec-k9 *)",
      "Bash(ssh gmktec-k9 \"*\")",
      "Bash(ssh root@gmktec-k9 \"*\")",
      "Bash(ssh gmktec-k9 '*')",
      "Bash(ssh root@gmktec-k9 '*')",
      "Bash(ssh * 'cd * && *')",
      "Bash(ssh * \"cd * && *\")",
      "Bash(ssh * \"bash -s\" << *)",
      "Bash(ssh * \"sudo *\")",
      
      "Bash(scp * root@gmktec-k9:*)",
      "Bash(scp root@gmktec-k9:* *)",
      "Bash(rsync *)",
      "Bash(rsync -avz *)",
      "Bash(rsync -avz --exclude=* *)",
      "Bash(rsync -avz --delete *)",
      
      "Bash(git status*)",
      "Bash(git add *)",
      "Bash(git add .*)",
      "Bash(git add -A*)",
      "Bash(git add -u*)",
      "Bash(git commit -m *)",
      "Bash(git commit -am *)",
      "Bash(git commit --amend*)",
      "Bash(git push*)",
      "Bash(git push origin *)",
      "Bash(git push -u origin *)",
      "Bash(git pull*)",
      "Bash(git pull origin *)",
      "Bash(git fetch*)",
      "Bash(git fetch --all*)",
      "Bash(git log*)",
      "Bash(git log --oneline*)",
      "Bash(git log --graph*)",
      "Bash(git diff*)",
      "Bash(git diff --staged*)",
      "Bash(git diff HEAD*)",
      "Bash(git checkout *)",
      "Bash(git checkout -b *)",
      "Bash(git branch*)",
      "Bash(git branch -a*)",
      "Bash(git branch -d *)",
      "Bash(git branch -D *)",
      "Bash(git merge *)",
      "Bash(git rebase *)",
      "Bash(git stash*)",
      "Bash(git stash pop*)",
      "Bash(git stash list*)",
      "Bash(git remote *)",
      "Bash(git remote -v*)",
      "Bash(git remote add *)",
      "Bash(git remote set-url *)",
      "Bash(git config *)",
      "Bash(git reset *)",
      "Bash(git clean *)",
      "Bash(git tag *)",
      "Bash(git show *)",
      "Bash(git blame *)",
      "Bash(git clone *)",
      "Bash(git init*)",
      
      "Bash(ls*)",
      "Bash(ls -la*)",
      "Bash(ls -l*)",
      "Bash(ls -a*)",
      "Bash(ls -lh*)",
      "Bash(ls -la */)",
      "Bash(ll*)",
      "Bash(cat *)",
      "Bash(cat -n *)",
      "Bash(less *)",
      "Bash(more *)",
      "Bash(head *)",
      "Bash(head -n *)",
      "Bash(head -*)",
      "Bash(tail *)",
      "Bash(tail -n *)",
      "Bash(tail -*)",
      "Bash(tail -f *)",
      "Bash(grep *)",
      "Bash(grep -r *)",
      "Bash(grep -i *)",
      "Bash(grep -n *)",
      "Bash(grep -E *)",
      "Bash(grep -v *)",
      "Bash(grep -A* -B* *)",
      "Bash(egrep *)",
      "Bash(fgrep *)",
      "Bash(sed *)",
      "Bash(sed -i *)",
      "Bash(sed -n *)",
      "Bash(sed -e *)",
      "Bash(awk *)",
      "Bash(cut *)",
      "Bash(sort *)",
      "Bash(uniq *)",
      "Bash(wc *)",
      "Bash(wc -l *)",
      "Bash(find *)",
      "Bash(find . -name *)",
      "Bash(find . -type *)",
      "Bash(find . -path *)",
      "Bash(cp *)",
      "Bash(cp -r *)",
      "Bash(cp -a *)",
      "Bash(cp -p *)",
      "Bash(mv *)",
      "Bash(rm *)",
      "Bash(rm -f *)",
      "Bash(rm -r *)",
      "Bash(rm -rf *)",
      "Bash(mkdir *)",
      "Bash(mkdir -p *)",
      "Bash(rmdir *)",
      "Bash(touch *)",
      "Bash(chmod *)",
      "Bash(chown *)",
      "Bash(diff *)",
      "Bash(tree *)",
      "Bash(pwd*)",
      "Bash(cd *)",
      "Bash(cd * && *)",
      "Bash(pushd *)",
      "Bash(popd*)",
      "Bash(basename *)",
      "Bash(dirname *)",
      "Bash(realpath *)",
      "Bash(readlink *)",
      
      "Bash(curl *)",
      "Bash(curl -s *)",
      "Bash(curl -S *)",
      "Bash(curl -f *)",
      "Bash(curl -L *)",
      "Bash(curl -o *)",
      "Bash(curl -O *)",
      "Bash(curl -X GET *)",
      "Bash(curl -X POST *)",
      "Bash(curl -X PUT *)",
      "Bash(curl -X DELETE *)",
      "Bash(curl -X PATCH *)",
      "Bash(curl -H \"*\" *)",
      "Bash(curl -H '*' *)",
      "Bash(curl -d *)",
      "Bash(curl --data *)",
      "Bash(curl --data-binary *)",
      "Bash(curl --header *)",
      "Bash(curl --request *)",
      "Bash(curl -u *)",
      "Bash(curl --user *)",
      "Bash(curl -w *)",
      "Bash(curl --write-out *)",
      "Bash(curl -v *)",
      "Bash(curl --verbose *)",
      "Bash(curl -k *)",
      "Bash(curl --insecure *)",
      "Bash(curl -i *)",
      "Bash(curl --include *)",
      "Bash(curl * | jq*)",
      "Bash(curl * | grep*)",
      "Bash(curl * | head*)",
      "Bash(curl * | tail*)",
      
      "Bash(npm *)",
      "Bash(npm install*)",
      "Bash(npm install --save*)",
      "Bash(npm install --save-dev*)",
      "Bash(npm install -g*)",
      "Bash(npm ci*)",
      "Bash(npm run *)",
      "Bash(npm test*)",
      "Bash(npm start*)",
      "Bash(npm build*)",
      "Bash(npm run build*)",
      "Bash(npm run test*)",
      "Bash(npm run dev*)",
      "Bash(npm run lint*)",
      "Bash(npm list*)",
      "Bash(npm update*)",
      "Bash(npm audit*)",
      "Bash(npm fund*)",
      "Bash(npm init*)",
      "Bash(npx *)",
      "Bash(node *)",
      "Bash(node -v*)",
      "Bash(node --version*)",
      "Bash(node -e *)",
      "Bash(node scripts/*)",
      "Bash(node *.js*)",
      
      "Bash(cargo *)",
      "Bash(cargo build*)",
      "Bash(cargo run*)",
      "Bash(cargo test*)",
      "Bash(cargo check*)",
      "Bash(cargo fmt*)",
      "Bash(cargo clippy*)",
      "Bash(rustc *)",
      "Bash(rustup *)",
      
      "Bash(go *)",
      "Bash(go build*)",
      "Bash(go run*)",
      "Bash(go test*)",
      "Bash(go get*)",
      "Bash(go mod*)",
      "Bash(go fmt*)",
      "Bash(go vet*)",
      
      "Bash(gem *)",
      "Bash(gem install*)",
      "Bash(gem list*)",
      "Bash(bundle *)",
      "Bash(bundle install*)",
      "Bash(bundle exec*)",
      "Bash(ruby *)",
      "Bash(rake *)",
      
      "Bash(java *)",
      "Bash(javac *)",
      "Bash(mvn *)",
      "Bash(mvn clean*)",
      "Bash(mvn install*)",
      "Bash(mvn test*)",
      "Bash(gradle *)",
      "Bash(gradle build*)",
      "Bash(gradle test*)",
      
      "Bash(php *)",
      "Bash(php -r *)",
      "Bash(php -v*)",
      "Bash(composer *)",
      "Bash(composer install*)",
      "Bash(composer update*)",
      "Bash(composer require*)",
      
      "Bash(bun *)",
      "Bash(bun install*)",
      "Bash(bun run*)",
      "Bash(bun test*)",
      "Bash(bun build*)",
      "Bash(bunx *)",
      
      "Bash(deno *)",
      "Bash(deno run*)",
      "Bash(deno test*)",
      "Bash(deno fmt*)",
      "Bash(deno lint*)",
      "Bash(deno compile*)",
      
      "Bash(echo $*)",
      "Bash(echo \"$*\")",
      "Bash(echo '$*')",
      "Bash(echo *)",
      "Bash(export *)",
      "Bash(unset *)",
      "Bash(env*)",
      "Bash(env | grep*)",
      "Bash(printenv*)",
      "Bash(printenv | grep*)",
      "Bash(set*)",
      "Bash(source *)",
      "Bash(. *)",
      
      "Bash(STACK_MANAGER_* npm *)",
      "Bash(N8N_* npm *)",
      "Bash(POSTGRES_* npm *)",
      "Bash(NODE_ENV=* npm *)",
      
      "Bash(jq *)",
      "Bash(jq .*)",
      "Bash(jq -r *)",
      "Bash(jq -c *)",
      "Bash(jq -s *)",
      "Bash(jq --tab*)",
      "Bash(* | jq)",
      "Bash(* | jq .)",
      "Bash(* | jq -r *)",
      "Bash(* | jq '.*')",
      "Bash(* | jq \".*\")",
      "Bash(* | jq '. | *')",
      "Bash(yq *)",
      "Bash(yq eval *)",
      "Bash(yq -i *)",
      "Bash(* | yq*)",
      
      "Bash(ps *)",
      "Bash(ps aux*)",
      "Bash(ps -ef*)",
      "Bash(ps | grep*)",
      "Bash(pgrep *)",
      "Bash(kill *)",
      "Bash(kill -9 *)",
      "Bash(pkill *)",
      "Bash(killall *)",
      "Bash(jobs*)",
      "Bash(fg*)",
      "Bash(bg*)",
      "Bash(nohup *)",
      "Bash(sleep *)",
      "Bash(wait*)",
      
      "Bash(date*)",
      "Bash(date +*)",
      "Bash(whoami*)",
      "Bash(hostname*)",
      "Bash(uname *)",
      "Bash(which *)",
      "Bash(whereis *)",
      "Bash(id*)",
      "Bash(groups*)",
      "Bash(df *)",
      "Bash(du *)",
      "Bash(free*)",
      "Bash(top*)",
      "Bash(htop*)",
      "Bash(uptime*)",
      "Bash(w*)",
      "Bash(who*)",
      "Bash(last*)",
      "Bash(history*)",
      "Bash(alias*)",
      "Bash(type *)",
      
      "Bash(ping *)",
      "Bash(netstat *)",
      "Bash(ss *)",
      "Bash(lsof *)",
      "Bash(lsof -i *)",
      "Bash(sudo lsof *)",
      "Bash(nslookup *)",
      "Bash(dig *)",
      "Bash(host *)",
      "Bash(wget *)",
      "Bash(nc -z *)",
      "Bash(telnet *)",
      "Bash(traceroute *)",
      "Bash(ip *)",
      "Bash(ifconfig*)",
      
      "Bash(apt *)",
      "Bash(apt-get *)",
      "Bash(apt update*)",
      "Bash(apt install *)",
      "Bash(apt remove *)",
      "Bash(apt search *)",
      "Bash(apt list *)",
      "Bash(sudo apt *)",
      "Bash(sudo apt-get *)",
      "Bash(sudo apt update*)",
      "Bash(sudo apt install *)",
      "Bash(sudo apt upgrade*)",
      "Bash(sudo apt autoremove*)",
      "Bash(sudo apt autoclean*)",
      "Bash(dpkg *)",
      "Bash(dpkg -l*)",
      "Bash(dpkg -i *)",
      "Bash(sudo dpkg -i *)",
      "Bash(snap *)",
      "Bash(sudo snap install *)",
      "Bash(sudo snap remove *)",
      "Bash(brew *)",
      "Bash(brew install *)",
      "Bash(brew update*)",
      "Bash(brew upgrade*)",
      "Bash(brew list*)",
      "Bash(yum *)",
      "Bash(sudo yum install *)",
      "Bash(sudo yum update*)",
      "Bash(dnf *)",
      "Bash(sudo dnf install *)",
      "Bash(sudo dnf update*)",
      
      "Bash(openssl *)",
      "Bash(openssl rand *)",
      "Bash(openssl x509 *)",
      "Bash(openssl req *)",
      "Bash(openssl genrsa *)",
      
      "Bash(gh *)",
      "Bash(gh auth *)",
      "Bash(gh auth login*)",
      "Bash(gh auth status*)",
      "Bash(gh repo *)",
      "Bash(gh repo view*)",
      "Bash(gh repo list*)",
      "Bash(gh repo clone*)",
      "Bash(gh repo create*)",
      "Bash(gh pr *)",
      "Bash(gh pr create*)",
      "Bash(gh pr list*)",
      "Bash(gh pr view*)",
      "Bash(gh issue *)",
      "Bash(gh api *)",
      "Bash(gh workflow *)",
      "Bash(gh release *)",
      
      "Bash(bash *)",
      "Bash(sh *)",
      "Bash(./deploy-latest-updates.sh*)",
      "Bash(./*.sh*)",
      "Bash(./scripts/*)",
      "Bash(bash scripts/*)",
      "Bash(sh scripts/*)",
      "Bash(source scripts/*)",
      
      "Bash(* | *)",
      "Bash(* > *)",
      "Bash(* >> *)",
      "Bash(* 2>&1*)",
      "Bash(* 2> *)",
      "Bash(* < *)",
      "Bash(* << *)",
      "Bash(* <<< *)",
      "Bash(* && *)",
      "Bash(* || *)",
      "Bash(* ; *)",
      
      "Bash(sudo docker *)",
      "Bash(sudo systemctl *)",
      "Bash(sudo journalctl *)",
      "Bash(sudo service *)",
      "Bash(sudo bash -c *)",
      "Bash(sudo sh -c *)",
      
      "Bash(systemctl *)",
      "Bash(systemctl status *)",
      "Bash(systemctl start *)",
      "Bash(systemctl stop *)",
      "Bash(systemctl restart *)",
      "Bash(journalctl *)",
      "Bash(journalctl -u *)",
      "Bash(journalctl -f*)",
      "Bash(journalctl --since *)",
      
      "Bash(tar *)",
      "Bash(tar -czf *)",
      "Bash(tar -xzf *)",
      "Bash(tar -cjf *)",
      "Bash(tar -xjf *)",
      "Bash(tar -tvf *)",
      "Bash(tar --exclude=* *)",
      "Bash(gzip *)",
      "Bash(gzip -d *)",
      "Bash(gzip -9 *)",
      "Bash(gunzip *)",
      "Bash(zip *)",
      "Bash(zip -r *)",
      "Bash(zip -u *)",
      "Bash(zip -d *)",
      "Bash(unzip *)",
      "Bash(unzip -l *)",
      "Bash(unzip -o *)",
      "Bash(unzip -d * *)",
      "Bash(7z *)",
      "Bash(7z a *)",
      "Bash(7z x *)",
      "Bash(7z l *)",
      "Bash(bzip2 *)",
      "Bash(bunzip2 *)",
      "Bash(xz *)",
      "Bash(unxz *)",
      
      "Bash(tr *)",
      "Bash(fold *)",
      "Bash(column *)",
      "Bash(paste *)",
      "Bash(join *)",
      "Bash(split *)",
      "Bash(csplit *)",
      "Bash(tee *)",
      "Bash(xargs *)",
      
      "Bash(printf *)",
      "Bash(test *)",
      "Bash([ *)",
      "Bash([[ *)",
      "Bash(true*)",
      "Bash(false*)",
      "Bash(yes*)",
      "Bash(seq *)",
      "Bash(shuf *)",
      "Bash(bc *)",
      "Bash(expr *)",
      
      "Bash(open -a Docker*)",
      "Bash(open -a *)",
      "Bash(timeout *)",
      "Bash(time *)",
      "Bash(watch *)",
      
      "Bash(psql *)",
      "Bash(psql -h * -U * -d *)",
      "Bash(psql -c *)",
      "Bash(psql -f *)",
      "Bash(pg_dump *)",
      "Bash(pg_restore *)",
      "Bash(pg_dumpall*)",
      "Bash(createdb *)",
      "Bash(dropdb *)",
      "Bash(docker exec * psql *)",
      "Bash(docker exec * pg_dump *)",
      "Bash(docker exec * pg_restore *)",
      
      "Bash(mysql *)",
      "Bash(mysql -u * -p*)",
      "Bash(mysql -e *)",
      "Bash(mysqldump *)",
      "Bash(mysqlimport *)",
      "Bash(mysqladmin *)",
      "Bash(docker exec * mysql *)",
      "Bash(docker exec * mysqldump *)",
      
      "Bash(mongo *)",
      "Bash(mongosh *)",
      "Bash(mongodump *)",
      "Bash(mongorestore *)",
      "Bash(mongoexport *)",
      "Bash(mongoimport *)",
      "Bash(mongod *)",
      "Bash(docker exec * mongo *)",
      "Bash(docker exec * mongosh *)",
      
      "Bash(sqlite3 *)",
      "Bash(sqlite3 * .dump*)",
      "Bash(sqlite3 * < *)",
      "Bash(sqlite3 * '.tables'*)",
      "Bash(sqlite3 * '.schema'*)",
      
      "Bash(redis-cli *)",
      "Bash(redis-cli -h * -p *)",
      "Bash(redis-cli ping*)",
      "Bash(redis-cli info*)",
      "Bash(redis-cli monitor*)",
      "Bash(docker exec * redis-cli *)",
      
      "Bash(openssl rand -hex 32*)",
      "Bash(openssl rand -base64 *)",
      "Bash(uuidgen*)",
      "Bash(pwgen *)",
      
      "Bash(openssl x509 -noout -text -in *)",
      "Bash(openssl x509 -noout -dates -in *)",
      "Bash(openssl x509 -noout -subject -in *)",
      "Bash(openssl verify *)",
      
      "Bash(npm test -- --coverage*)",
      "Bash(npm test -- --watch*)",
      "Bash(npm test -- --no-coverage*)",
      "Bash(jest *)",
      "Bash(npx jest *)",
      "Bash(npm run test:*)",
      
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pip *)",
      "Bash(pip3 *)",
      "Bash(python -m *)",
      "Bash(python3 -m *)",
      
      "Bash(nvm *)",
      "Bash(nvm install *)",
      "Bash(nvm use *)",
      "Bash(nvm ls*)",
      "Bash(nvm alias *)",
      "Bash(nvm current*)",
      "Bash(pyenv *)",
      "Bash(pyenv install *)",
      "Bash(pyenv global *)",
      "Bash(pyenv local *)",
      "Bash(pyenv versions*)",
      "Bash(pyenv which *)",
      "Bash(rbenv *)",
      "Bash(rbenv install *)",
      "Bash(rbenv global *)",
      "Bash(rbenv local *)",
      "Bash(rbenv versions*)",
      "Bash(rbenv which *)",
      "Bash(rvm *)",
      "Bash(rvm install *)",
      "Bash(rvm use *)",
      "Bash(rvm list*)",
      "Bash(asdf *)",
      "Bash(asdf install *)",
      "Bash(asdf global *)",
      "Bash(asdf local *)",
      "Bash(asdf list*)",
      
      "Bash(direnv *)",
      "Bash(direnv allow*)",
      "Bash(direnv deny*)",
      "Bash(direnv status*)",
      "Bash(direnv reload*)",
      
      "Bash(tmux *)",
      "Bash(tmux new*)",
      "Bash(tmux attach*)",
      "Bash(tmux ls*)",
      "Bash(tmux kill-session*)",
      "Bash(tmux send-keys *)",
      "Bash(tmux capture-pane*)",
      "Bash(screen *)",
      "Bash(screen -S *)",
      "Bash(screen -r *)",
      "Bash(screen -ls*)",
      "Bash(screen -X *)",
      
      "Bash(lsof -i :*)",
      "Bash(sudo lsof -i :*)",
      "Bash(netstat -an | grep *)",
      "Bash(ss -an | grep *)",
      "Bash(nc -zv * *)",
      
      "Bash(tail -f logs/*)",
      "Bash(tail -f *.log*)",
      "Bash(grep -i error logs/*)",
      "Bash(grep -i warn logs/*)",
      "Bash(journalctl -xeu *)",
      
      "Bash(df -h*)",
      "Bash(du -sh *)",
      "Bash(du -h --max-depth=*)",
      "Bash(free -m*)",
      "Bash(free -h*)",
      
      "Bash(docker volume ls | grep *)",
      "Bash(docker volume inspect * | jq*)",
      "Bash(docker volume rm $(docker volume ls -q)*)",
      
      "Bash(for * in *; do *; done*)",
      "Bash(while *; do *; done*)",
      "Bash(if *; then *; fi*)",
      "Bash(case * in *) *;; esac*)",
      
      "Bash(* &)",
      "Bash(nohup * &)",
      "Bash(* > /dev/null 2>&1 &)",
      "Bash(disown*)",
      
      "Bash(echo * | tr *)",
      "Bash(echo * | sed *)",
      "Bash(echo * | awk *)",
      "Bash(echo * | cut *)",
      "Bash(echo * | base64*)",
      "Bash(echo * | base64 -d*)",
      
      "Bash(http-server *)",
      "Bash(python -m http.server *)",
      "Bash(python3 -m http.server *)",
      "Bash(npx http-server *)",
      
      "Bash(make *)",
      "Bash(make clean*)",
      "Bash(make build*)",
      "Bash(make install*)",
      "Bash(make test*)",
      
      "Bash(yarn *)",
      "Bash(yarn install*)",
      "Bash(yarn add *)",
      "Bash(yarn remove *)",
      "Bash(yarn run *)",
      "Bash(yarn test*)",
      "Bash(yarn build*)",
      
      "Bash(pnpm *)",
      "Bash(pnpm install*)",
      "Bash(pnpm add *)",
      "Bash(pnpm run *)",
      
      "Bash(cat .env*)",
      "Bash(grep * .env*)",
      "Bash(echo * >> .env*)",
      "Bash(cp .env.example .env*)",
      "Bash(cp .env .env.backup*)",
      
      "Bash(docker network *)",
      "Bash(docker network ls*)",
      "Bash(docker network inspect *)",
      "Bash(docker network create *)",
      "Bash(docker network rm *)",
      
      "Bash(curl -f http://localhost:*/health*)",
      "Bash(curl -f http://localhost:*/api/health*)",
      "Bash(curl -f http://localhost:*/metrics*)",
      "Bash(wget -O- http://localhost:*/health*)",
      
      "Bash(git remote show origin*)",
      "Bash(git ls-remote *)",
      "Bash(git fetch --prune*)",
      "Bash(git gc*)",
      "Bash(git reflog*)",
      
      "Bash(ssh-keygen *)",
      "Bash(ssh-add *)",
      "Bash(ssh-keyscan *)",
      "Bash(ssh-copy-id *)",
      
      "Bash(timedatectl*)",
      "Bash(date -u*)",
      "Bash(TZ=* date*)",
      
      "Bash(md5sum *)",
      "Bash(sha1sum *)",
      "Bash(sha256sum *)",
      "Bash(sha512sum *)",
      "Bash(shasum *)",
      
      "Bash(tar -czf * *)",
      "Bash(tar -xzf *)",
      "Bash(tar -tvf *)",
      "Bash(zip -r * *)",
      "Bash(unzip -l *)",
      
      "Bash(stat *)",
      "Bash(getfacl *)",
      "Bash(file *)",
      "Bash(file -b *)",
      
      "Bash(npm ls *)",
      "Bash(npm info *)",
      "Bash(npm view *)",
      "Bash(npm outdated*)",
      
      "Bash(pidof *)",
      "Bash(pstree *)",
      "Bash(lsof -p *)",
      "Bash(strace -p *)",
      
      "Bash(crontab -l*)",
      "Bash(crontab -e*)",
      "Bash(cat /etc/cron*)",
      
      "Bash(avahi-browse *)",
      "Bash(mdns-scan*)",
      
      "Bash(iotop*)",
      "Bash(iftop*)",
      "Bash(nethogs*)",
      "Bash(dstat*)",
      "Bash(vmstat*)",
      "Bash(iostat*)",
      
      "Bash(nano -v *)",
      "Bash(vim -R *)",
      "Bash(view *)",
      "Bash(less +F *)",
      
      "Read(**)",
      "Edit(**)",
      "MultiEdit(**)",
      "Write(**)",
      "Glob(**)",
      "Grep(**)",
      "LS(**)",
      
      "NotebookRead(**)",
      "NotebookEdit(**)",
      
      "WebFetch(domain:docs.anthropic.com)",
      "WebFetch(domain:localhost)",
      "WebFetch(domain:127.0.0.1)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:n8n.io)",
      "WebFetch(domain:*.nextsteptek.com)",
      "WebFetch(domain:gmktec-k9)",
      "WebFetch(domain:api.openai.com)",
      "WebFetch(domain:api.anthropic.com)",
      "WebSearch(**)",
      
      "Bash(aws *)",
      "Bash(aws s3 *)",
      "Bash(aws ec2 *)",
      "Bash(aws lambda *)",
      "Bash(aws dynamodb *)",
      "Bash(aws rds *)",
      "Bash(aws iam *)",
      "Bash(aws cloudformation *)",
      "Bash(aws configure*)",
      "Bash(aws sts *)",
      "Bash(aws logs *)",
      "Bash(aws ecr *)",
      "Bash(aws ecs *)",
      "Bash(aws eks *)",
      
      "Bash(gcloud *)",
      "Bash(gcloud auth *)",
      "Bash(gcloud config *)",
      "Bash(gcloud compute *)",
      "Bash(gcloud container *)",
      "Bash(gcloud app *)",
      "Bash(gcloud functions *)",
      "Bash(gcloud storage *)",
      "Bash(gcloud sql *)",
      "Bash(gcloud run *)",
      "Bash(gcloud projects *)",
      "Bash(gcloud services *)",
      "Bash(gsutil *)",
      
      "Bash(az *)",
      "Bash(az login*)",
      "Bash(az account *)",
      "Bash(az group *)",
      "Bash(az vm *)",
      "Bash(az storage *)",
      "Bash(az webapp *)",
      "Bash(az functionapp *)",
      "Bash(az sql *)",
      "Bash(az aks *)",
      "Bash(az acr *)",
      "Bash(az keyvault *)",
      
      "Bash(vercel *)",
      "Bash(vercel deploy*)",
      "Bash(vercel dev*)",
      "Bash(vercel build*)",
      "Bash(vercel env *)",
      "Bash(vercel secrets *)",
      "Bash(vercel domains *)",
      "Bash(vercel logs*)",
      "Bash(vc *)",
      
      "Bash(netlify *)",
      "Bash(netlify deploy*)",
      "Bash(netlify dev*)",
      "Bash(netlify build*)",
      "Bash(netlify functions *)",
      "Bash(netlify env *)",
      "Bash(netlify sites *)",
      "Bash(netlify status*)",
      "Bash(ntl *)",
      
      "Bash(heroku *)",
      "Bash(heroku create*)",
      "Bash(heroku deploy*)",
      "Bash(heroku logs*)",
      "Bash(heroku ps*)",
      "Bash(heroku config*)",
      "Bash(heroku addons*)",
      "Bash(heroku run *)",
      "Bash(heroku domains*)",
      "Bash(heroku releases*)",
      
      "TodoRead()",
      "TodoWrite(**)",
      
      "Task(**)",
      
      "Bash(claude *)",
      "Bash(claude config *)",
      "Bash(claude code *)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(rm -rf /)",
      "Bash(sudo rm -rf /*)",
      "Bash(sudo rm -rf /)",
      "Bash(dd if=/dev/zero of=/dev/*)",
      "Bash(dd if=/dev/random of=/dev/*)",
      "Bash(mkfs*)",
      "Bash(fdisk*)",
      "Bash(parted*)",
      
      "Bash(:(){ :|:& };:*)",
      "Bash(*fork*bomb*)",
      
      "Bash(> /dev/sda*)",
      "Bash(> /dev/nvme*)",
      "Bash(> /dev/sd*)",
      "Bash(cat /dev/urandom > *)",
      
      "Bash(* | nc -l*)",
      "Bash(* | netcat -l*)",
      "Bash(* | socat *)",
      "Bash(* | base64 -d | sh*)",
      "Bash(* | base64 -d | bash*)",
      "Bash(curl * | sh*)",
      "Bash(curl * | bash*)",
      "Bash(wget * | sh*)",
      "Bash(wget * | bash*)",
      
      "Bash(sudo passwd*)",
      "Bash(passwd*)",
      "Bash(sudo useradd*)",
      "Bash(sudo userdel*)",
      "Bash(sudo usermod*)",
      "Bash(sudo groupadd*)",
      "Bash(sudo groupdel*)",
      "Bash(sudo adduser*)",
      "Bash(sudo deluser*)",
      
      "Bash(sudo chmod 777 /*)",
      "Bash(sudo chown * /*)",
      "Bash(sudo rm /etc/*)",
      "Bash(sudo rm -rf /etc/*)",
      "Bash(sudo rm /bin/*)",
      "Bash(sudo rm /usr/*)",
      "Bash(sudo > /etc/*)",
      
      "Bash(nc -l*)",
      "Bash(netcat -l*)",
      "Bash(socat*)",
      "Bash(nmap*)",
      "Bash(masscan*)",
      
      "Bash(*xmrig*)",
      "Bash(*monero*)",
      "Bash(*bitcoin*)",
      "Bash(*miner*)",
      
      "Bash(git push --force origin master*)",
      "Bash(git push --force origin main*)",
      "Bash(git push -f origin master*)",
      "Bash(git push -f origin main*)",
      "Bash(git reset --hard origin/master*)",
      "Bash(git reset --hard origin/main*)",
      
      "Bash(cat ~/.aws/*)",
      "Bash(cat ~/.ssh/id_*)",
      "Bash(cat /root/.ssh/*)",
      
      "Bash(env | base64*)",
      "Bash(printenv | base64*)",
      "Bash(set | base64*)",
      
      "Bash(bash -i >& /dev/tcp/*)",
      "Bash(sh -i >& /dev/tcp/*)",
      "Bash(python -c 'import socket*)",
      "Bash(php -r '$sock*)",
      "Bash(ruby -rsocket*)",
      "Bash(perl -e 'use Socket*)",
      
      "Bash(docker run --privileged *)",
      "Bash(docker run --pid=host *)",
      "Bash(docker run --net=host *)",
      "Bash(docker run -v /:/host *)",
      "Bash(docker run -v /etc:/etc *)",
      "Bash(docker run -v /var/run/docker.sock:/var/run/docker.sock *)",
      
      "Bash(history | grep -i password*)",
      "Bash(history | grep -i token*)",
      "Bash(history | grep -i secret*)",
      "Bash(history | grep -i key*)",
      "Bash(grep -r password /etc/*)",
      "Bash(grep -r token /etc/*)",
      "Bash(find / -name id_rsa*)",
      "Bash(find / -name *.key*)",
      "Bash(find / -name *.pem*)",
      
      "Bash(shutdown*)",
      "Bash(reboot*)",
      "Bash(halt*)",
      "Bash(poweroff*)",
      "Bash(init 0*)",
      "Bash(init 6*)",
      "Bash(sudo shutdown*)",
      "Bash(sudo reboot*)",
      
      "Bash(sudo ufw disable*)",
      "Bash(sudo iptables -F*)",
      "Bash(sudo iptables --flush*)",
      "Bash(sudo systemctl stop firewalld*)",
      "Bash(sudo service iptables stop*)",
      
      "Bash(curl * | sudo *)",
      "Bash(wget * | sudo *)",
      "Bash(curl -s * | sh*)",
      "Bash(wget -qO- * | sh*)",
      
      "Bash(rm /var/log/*)",
      "Bash(rm -rf /var/log/*)",
      "Bash(> /var/log/*)",
      "Bash(echo > /var/log/*)",
      "Bash(truncate -s 0 /var/log/*)",
      
      "Bash(npm install -g * --unsafe-perm*)",
      "Bash(pip install * --break-system-packages*)",
      "Bash(gem install * --no-user-install*)",
      
      "Bash(insmod *)",
      "Bash(rmmod *)",
      "Bash(modprobe *)",
      "Bash(sysctl -w *)",
      
      "Bash(chmod -R 777 /*)",
      "Bash(chmod 777 /etc/*)",
      "Bash(chmod 777 /bin/*)",
      "Bash(chmod 777 /usr/*)",
      "Bash(chown -R * /*)",
      
      "Bash(*bitcoin-cli*)",
      "Bash(*ethereum*)",
      "Bash(*wallet.dat*)",
      "Bash(*privatekey*)",
      
      "Bash(find / -type f -delete*)",
      "Bash(find / -type d -delete*)",
      "Bash(rm -rf /home/*)",
      "Bash(rm -rf /var/*)",
      "Bash(rm -rf /opt/*)",
      
      "Bash(gdb -p *)",
      "Bash(ptrace *)",
      "Bash(LD_PRELOAD=*)",
      
      "Bash(sudo -l*)",
      "Bash(sudo -V*)",
      "Bash(sudo su*)",
      "Bash(sudo su -*)",
      "Bash(sudo -i*)",
      "Bash(pkexec *)",
      
      "Bash(export PATH=*)",
      "Bash(export LD_LIBRARY_PATH=*)",
      "Bash(export PYTHONPATH=*)",
      
      "Bash(nsenter *)",
      "Bash(docker run --cap-add=ALL *)",
      "Bash(docker run --security-opt *)",
      
      "Bash(systemctl mask *)",
      "Bash(systemctl disable *)",
      "Bash(systemctl daemon-reload*)",
      
      "Bash(curl http://169.254.169.254/*)",
      "Bash(wget http://169.254.169.254/*)",
      "Bash(curl http://metadata.google.internal/*)",
      
      "Bash(exec < /dev/tcp/*)",
      "Bash(exec > /dev/tcp/*)",
      "Bash(exec 3<>/dev/tcp/*)"
    ]
  }
}
````
