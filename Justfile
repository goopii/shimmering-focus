set quiet := true

biome_bin := env("HOME") / ".local/share/nvim/mason/bin/biome"

#───────────────────────────────────────────────────────────────────────────────

# The Padua theme folder is symlinked to this repository.
personal-build-and-reload:
    npm run build
    env -u ELECTRON_RUN_AS_NODE obsidian vault=Padua eval 'code=app.customCss.reloadTheme()'

biome-check-and-format:
    {{ biome_bin }} check --write --error-on-warnings --log-kind="compact"
