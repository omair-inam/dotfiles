# README

## Installation directions

### Prerequisites

- **Xcode Command Line Tools, Rosetta 2, Homebrew, and Oh My Zsh** are installed by the
  first `chezmoi apply` (`run_before_00_bootstrap`). Homebrew asks you to press RETURN and enter your password once.
- **1Password** is installed automatically by `chezmoi apply`. After the first apply
  completes, open 1Password, sign in, and unlock it.
- **1Password Developer settings** — before your first git commit, open
  **1Password > Settings > Developer** and enable both of the following:
  - **Use the SSH Agent** — allows git to use SSH keys stored in 1Password for commit
    signing (`gpgsign = true` in the git config). Without this, every `git commit` will
    fail. Make sure your SSH key is added to the agent.
  - **Integrate with 1Password CLI** — lets the `op` CLI authenticate through the
    desktop app instead of requiring a separate sign-in. This is required for
    the `gh` CLI plugin (`op plugin run -- gh`).
- **Sign in to the Mac App Store** before running `chezmoi apply`. Open the App Store and
  sign in with your Apple ID. `chezmoi apply` uses `mas` to install Things 3 and Yubico
  Authenticator; if you are not signed in, `mas` will silently skip those installs.

### 1. Install chezmoi and apply dotfiles

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply --use-builtin-git=true omair-inam
```

This installs chezmoi into `./bin`, clones this repo, and runs the first apply.
`--use-builtin-git=true` makes chezmoi clone with its own git. On a Mac without Xcode
Command Line Tools, `/usr/bin/git` only opens the install dialog and exits with an error. The
bootstrap script installs Xcode Command Line Tools, Rosetta 2, Homebrew, Oh My Zsh,
Powerlevel10k, and the zsh plugins before any package is installed. Later applies use the
Homebrew `chezmoi` that the package step installs.

During `chezmoi apply` you will be prompted for three values (cached after first run):

| Prompt | Type | Purpose |
|---|---|---|
| `personal_device` | true/false | Enables personal apps and configs |
| `work_device` | true/false | Enables work apps and configs (DNAstack) |
| `email` | string | Used in git config |

`chezmoi apply` will then:
- Install Homebrew packages (formulae and casks) and Mac App Store apps (Things 3, Yubico Authenticator)
- Configure macOS defaults: Dock size 48px, Dock position by monitor count, reverse scroll
  direction to non-natural, then restart the Dock, Finder, and SystemUIServer (only when
  those defaults change)
- Install every tool declared in `~/.config/mise/config.toml` (node, and on work devices
  Java 21 + 24, terraform, and the npm and pipx tools)
- Install Chrome for Testing via `pnpm dlx @puppeteer/browsers`

> **Note:** The reversed scroll direction preference is written immediately but requires a
> **logout or restart** to take effect.

### 3. Post-install: commands requiring authentication

The following steps require the user to authenticate with their password and should be completed manually.

#### Enable FileVault disk encryption on macOS if it is not already enabled

To enable FileVault disk encryption on macOS, use the `fdesetup` command. This step requires superuser privileges.

```bash
sudo fdesetup status | grep -q "FileVault is On." || sudo fdesetup enable
```

#### Enable automatic macOS updates (work devices)

These need `sudo`, so they are not run by `chezmoi apply`:

```bash
sudo softwareupdate --background-critical
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled -bool true
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload -bool true
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate CriticalUpdateInstall -bool true
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticallyInstallMacOSUpdates -bool true
sudo defaults write /Library/Preferences/com.apple.commerce AutoUpdate -bool true
```

#### Update macOS software
You can start the software update process using the
terminal and the `softwareupdate` command.

1. To **list** the available updates to install...
   ```
   softwareupdate --list
   ```

2. To **install** the updates...
   ```
   softwareupdate --install --all
   ```

   :lock: You will probably be prompted for your Mac password

   Once all updates are downloaded, the command will finish (or appear to hang briefly).
   Check **System Settings > General > Software Update** to monitor progress and restart
   when prompted.

#### 1Password service-account tokens in the Keychain

Some repos authenticate `op` non-interactively from their `.envrc` using a 1Password
service-account token read out of the login Keychain. `chezmoi apply` keeps those items
in sync from `home/.chezmoidata/onepassword.toml`, so there is nothing to paste by hand.

The first apply on a new machine needs 1Password unlocked with **Integrate with
1Password CLI** enabled, and you have to approve the authorization prompt. If it was
locked, the apply prints what to do and carries on. Run `chezmoi apply` again once
1Password is ready.

#### Set up GitHub CLI authentication via 1Password

The `gh` CLI is authenticated through the 1Password shell plugin (`op plugin run -- gh`).
To configure it for this repo with your personal GitHub account:

```bash
cd ~/.local/share/chezmoi
op plugin init gh --account my.1password.com
```

When prompted, select your personal GitHub PAT and choose
**"Use automatically when in this directory or subdirectories"**.

Then fix the file permissions — the `op` CLI silently ignores configs that are world-readable:

```bash
chmod 600 .op/plugins/gh.json
```

Verify it works:

```bash
op plugin run -- gh auth status
```

> **Note:** The `.op/` directory is gitignored (machine-specific). This setup must be
> repeated on each new machine.

#### Reactivate software licenses

These apps have per-machine license activations that were deactivated before the wipe.
After they are installed, re-enter or reactivate their license keys:

- **Superkey** — manual install required (not in Homebrew); re-enter license key
- **Rectangle Pro** — re-enter license key
- **CleanShot** — re-enter license key
- **Aptakube** — re-enter license key
- **DaisyDisk** — manual install required (not in Homebrew); re-enter license key
- **IntelliJ IDEA** — sign in with JetBrains account

> License keys are stored in 1Password.

