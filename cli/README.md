# 🎓 Professor Profiler CLI

The official terminal interface for the Professor Profiler multi-agent AI system.

## 🚀 Installation

From the `cli` directory, run:
```bash
./install.sh
```
This will install dependencies, build the TypeScript code, and link the `prof` command globally.

## 💻 Commands

- `prof analyze <file>`: Analyze an exam paper using the multi-agent AI pipeline.
  - *Example*: `prof analyze @exam.pdf`
- `prof chat`: Start an interactive AI chat session.
- `prof agents`: List all available AI agents and their roles.
- `prof doctor`: Check your environment for compatibility.
- `prof config`: Manage CLI configuration.
- `prof history`: View session history.
- `prof models`: List available AI models.

## 🎨 Themes

You can customize the CLI startup banner using the `--theme` flag:
```bash
prof analyze @exam.pdf --theme cyberpunk
```
Available themes: `minimal`, `cyberpunk`, `hacker`, `ocean`, `sunset`.

## ⚙️ Configuration

Configuration is stored in `~/.professor-profiler/config.json`.
You can manage it via the `prof config` command:
```bash
prof config set theme hacker
prof config get provider
prof config list
```

## 🔄 Autocomplete

To enable shell autocomplete, add the following to your `~/.bashrc` or `~/.zshrc`:
```bash
eval "$(prof completion)"
```
*(Note: requires experimental commander completion support)*
