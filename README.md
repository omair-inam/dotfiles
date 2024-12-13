# README

## Sample commands

```bash
brew install --force --cask beyond-compare
brew install chezmoi
brew install --cask vscodium
brew install --cask qbserve
brew install --cask iterm2
brew install --cask rectangle-pro
brew install --cask google-chrome
```

## Notes
### Run Mac commands requiring authentication

The following steps require the user to authenticate with their password and should be completed manually

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

   Once the software updates are 100% downloaded,
   the terminal will "hang". At this point you should
   see the prompt and button to **reboot** the machine in
   **System Settings** > **General** > **Software Update**


### Apps pinned to older versions

* Beyond Compare 4
* Forklift 3

## Other docs

[Creating new casks](docs/casks.md)