# README

## Installation directions

### Prerequisites

- **Xcode Command Line Tools** will be installed automatically by Homebrew if not present.
  You may see a prompt to accept a license — click Install when asked.
- **1Password** is installed automatically by `chezmoi apply` on work devices. After the
  first apply completes, open 1Password, sign in, and unlock it, then run `chezmoi apply`
  a second time to populate secrets (NPM token, Maven credentials). See Step 2 below.
- **1Password Developer settings** — before your first git commit, open
  **1Password > Settings > Developer** and enable both of the following:
  - **Use the SSH Agent** — allows git to use SSH keys stored in 1Password for commit
    signing (`gpgsign = true` in the git config). Without this, every `git commit` will
    fail. Make sure your SSH key is added to the agent.
  - **Integrate with 1Password CLI** — lets the `op` CLI authenticate through the
    desktop app instead of requiring a separate sign-in. This is required for
    `chezmoi apply` to render templates that call `onepasswordRead` (NPM token, Maven
    credentials) and for the `gh` CLI plugin (`op plugin run -- gh`).
- **1Password must be signed in and unlocked** for Powerlevel10k and many zsh plugins to
  load correctly. The shell config (`.zshrc`) sources files rendered by chezmoi templates
  that depend on 1Password-backed secrets. If 1Password is locked or signed out when you
  open a new terminal, some plugins may fail to initialise or display errors.
- **Sign in to the Mac App Store** before running `chezmoi apply`. Open the App Store and
  sign in with your Apple ID. `chezmoi apply` uses `mas` to install Things 3 and Yubico
  Authenticator; if you are not signed in, `mas` will silently skip those installs.

### 1. Install Homebrew, chezmoi, Oh My Zsh, and plugins

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/omair-inam/dotfiles/refs/heads/main/install.sh)"
```

This script installs: Homebrew, Oh My Zsh, Powerlevel10k, zsh plugins (autosuggestions, forgit, completions, etc.), and chezmoi.

After the script completes, add Homebrew to your current shell session so that
`chezmoi` (and `brew`) are available:

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
```

This is only needed once — after `chezmoi apply` configures your shell, new
terminals will have Homebrew on PATH automatically.

### 2. Initialise and apply dotfiles

```bash
chezmoi init https://github.com/omair-inam/dotfiles.git
chezmoi apply
```

During `chezmoi apply` you will be prompted for three values (cached after first run):

| Prompt | Type | Purpose |
|---|---|---|
| `personal_device` | true/false | Enables personal apps and configs |
| `work_device` | true/false | Enables work apps and configs (DNAstack) |
| `email` | string | Used in git config |

`chezmoi apply` will then:
- Install Homebrew packages (formulae and casks) and Mac App Store apps (Things 3, Yubico Authenticator)
- Configure macOS defaults: move Dock to the left (size 48px), reverse scroll direction to non-natural
- Restart the Dock, Finder, and SystemUIServer to apply Dock changes
- Install Node.js LTS via mise (polyglot runtime manager)
- Install Chrome for Testing via `pnpm dlx @puppeteer/browsers`

> **Note:** The reversed scroll direction preference is written immediately but requires a
> **logout or restart** to take effect.
- Install pipx
- For work devices: enable automatic macOS updates, install Java 21 + 24 and Python 3.13.1 via asdf

**Work devices — second apply:** The first apply skips 1Password-backed secrets (NPM token,
Maven credentials) because the `op` CLI isn't available yet. After the first apply installs
1Password, open it, sign in, and unlock your vault, then run `chezmoi apply` again to
populate those secrets.

### 3. Post-install: commands requiring authentication

The following steps require the user to authenticate with their password and should be completed manually.

#### Enable FileVault disk encryption on macOS if it is not already enabled

To enable FileVault disk encryption on macOS, use the `fdesetup` command. This step requires superuser privileges.

```bash
sudo fdesetup status | grep -q "FileVault is On." || sudo fdesetup enable
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

   > **Note:** work devices have automatic macOS updates configured by `chezmoi apply`,
   > so this step is primarily for personal devices.

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

