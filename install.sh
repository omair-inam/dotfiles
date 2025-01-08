#!/bin/bash

set -eufo pipefail

echo ""
echo "🤚  This script will setup .dotfiles for you."
read -n 1 -r -s -p $'    Press any key to continue or Ctrl+C to abort...\n\n'


# Install Homebrew
command -v brew >/dev/null 2>&1 || \
  (echo '🍺  Installing Homebrew' && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")

# Install Oh My Zsh
if [ ! -f ~/.oh-my-zsh/oh-my-zsh.sh ]; then
  (echo '💰  Installing oh-my-zsh' && yes | sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)")
fi

# Function to install a plugin if it doesn't exist
install_plugin() {
  local plugin_name=$1
  local plugin_repo=$2
  local plugin_dir="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/$3"
  local clone_options=${4:-""}

  if [ ! -d "$plugin_dir" ]; then
    (echo "🚀  Installing $plugin_name" && git clone $clone_options "$plugin_repo" "$plugin_dir")
  fi
}

# Install Powerlevel10k
install_plugin "Powerlevel10k" "https://github.com/romkatv/powerlevel10k.git" "themes/powerlevel10k" "--depth=1"

# Install custom plugins
install_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions" "plugins/zsh-autosuggestions"
install_plugin "alias-tips" "https://github.com/djui/alias-tips.git" "plugins/alias-tips"
install_plugin "zsh-history-substring-search" "https://github.com/zsh-users/zsh-history-substring-search" "plugins/zsh-history-substring-search"
install_plugin "forgit" "https://github.com/wfxr/forgit.git" "plugins/forgit"
install_plugin "zsh-completions" "https://github.com/zsh-users/zsh-completions" "plugins/zsh-completions"
install_plugin "k" "https://github.com/supercrabtree/k" "plugins/k"
install_plugin "eza" https://github.com/z-shell/zsh-eza "plugins/zsh-eza"

# Install chezmoi
command -v chezmoi >/dev/null 2>&1 || \
  (echo '👊  Installing chezmoi' && brew install chezmoi)

if [ -d "$HOME/.local/share/chezmoi/.git" ]; then
  echo "🚸  chezmoi already initialized"
  echo "    Reinitialize with: 'chezmoi init https://github.com/omair-inam/dotfiles.git'"
else
  echo "🚀  Initialize dotfiles with:"
  echo "    chezmoi init https://github.com/omair-inam/dotfiles.git"
fi

echo ""
echo "Done."