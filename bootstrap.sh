#!/usr/bin/env bash

# ^ tells what interpreter the script should use

set -e

DOTFILES_DIR="$HOME/mingofiles"

PACKAGES=(
  "zsh"
  "git"
  "nvim"
  "kitty"
  "waybar"
  "niri"
  "fuzzel"
  "mako"
  "swaylock"
)

SYSTEM_PACKAGES=(
  "stow"
  "git"
  "zsh"
  "neovim"
  "waybar"
  "niri"
  "fuzzel"
  "mako"
  "swaylock"
  "ttf-meslo-nerd-font-powerlevel10k"
)

echo "==> 1. Updating system and installing base packages..."
if command -v yay &>/dev/null; then
  yay -S --needed --noconfirm "${SYSTEM_PACKAGES[@]}"
elif command -v pacman &>/dev/null; then
  sudo pacman -S --needed --noconfirm "${SYSTEM_PACKAGES[@]}"
else
  echo "Warning: Package manager not recognized. Skipping package installation."
fi

echo "==> 2. Restoring dotfiles symlinks with Stow..."
cd "$DOTFILES_DIR"

for package in "${PACKAGES[@]}"; do
  if [ -d "$package"]; then
    echo "Stowing $package..."
    #Unstow first to avoid conflicts, then stow
    stow -D "$package" 2>/dev/null || true
    stow "$package"
  else
    echo "Warning: Package folder '$package not found in $DOTFILES_DIR. Skipping."
  fi
done

echo "==> 3. Setting Zsh as default shell..."
if [ "$SHELL" != "$(which zsh)" ]; then
  chsh -s "$(which zsh)"
fi

echo "==> Setup complete! Log out and back in to apply all changes."
