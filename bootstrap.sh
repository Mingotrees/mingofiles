#!/usr/bin/env bash

# ^ tells what interpreter the script should use

set -euo pipefail

DOTFILES_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

PACKAGES=(
  "zsh"
  "git"
  "nvim"
  "kitty"
  "waybar"
  "wlogout"
  "niri"
  "fuzzel"
  "mako"
  "swaylock"
  "tmux"
  "fastfetch"
)

PACMAN_PACKAGES=(
  "stow"
  "git"
  "zsh"
  "neovim"
  "kitty"
  "waybar"
  "niri"
  "fuzzel"
  "mako"
  "blueman"
  "awww"
  "wireplumber"
  "pipewire-pulse"
  "playerctl"
  "brightnessctl"
  "btop"
  "networkmanager"
  "pavucontrol"
  "libpulse"
  "tmux"
  "wl-clipboard"
  "fastfetch"
  "ttf-hack-nerd"
  "ttf-jetbrains-mono-nerd"
)

AUR_PACKAGES=(
  "swaylock-effects"
  "wlogout"
  "zsh-theme-powerlevel10k-git"
)

echo "==> 1. Installing system packages..."
if command -v pacman &>/dev/null; then
  sudo pacman -S --needed --noconfirm "${PACMAN_PACKAGES[@]}"

  if command -v yay &>/dev/null; then
    yay -S --needed --noconfirm "${AUR_PACKAGES[@]}"
  else
    printf 'Warning: yay is not installed. Install these AUR packages manually: %s\n' "${AUR_PACKAGES[*]}"
  fi
else
  echo "Warning: pacman not found. Skipping package installation."
fi

echo "==> 2. Restoring dotfiles symlinks with Stow..."
cd "$DOTFILES_DIR"

for package in "${PACKAGES[@]}"; do
  if [ -d "$package" ]; then
    echo "Stowing $package..."
    stow --restow "$package"
  else
    echo "Warning: Package folder '$package' not found in $DOTFILES_DIR. Skipping."
  fi
done

echo "==> 3. Setting Zsh as default shell..."
if zsh_path="$(command -v zsh)"; then
  if [ "${SHELL:-}" != "$zsh_path" ]; then
    chsh -s "$zsh_path"
  fi
else
  echo "Warning: zsh not found. Default shell was not changed."
fi

echo "==> Setup complete! Log out and back in to apply all changes."
