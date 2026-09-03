# 🥭 Mingofiles

My personal Arch Linux configuration files, managed with **GNU Stow** and automated for fast deployment. Built for a Wayland-native workflow using **Niri**, **Waybar**, and **Kitty**.

---

## 🎨 System Overview

| Component | Tool |
| :--- | :--- |
| **OS** | Arch Linux |
| **Compositor / WM** | [Niri](https://github.com/YaLteR/niri) |
| **Bar** | [Waybar](https://github.com/Alexays/Waybar) |
| **Terminal** | [Kitty](https://sw.kovidgoyal.net/kitty/) |
| **Shell** | Zsh + [Powerlevel10k](https://github.com/romkatv/powerlevel10k) |
| **Editor** | Neovim |
| **Launcher** | [Fuzzel](https://codeberg.org/dnkl/fuzzel) |
| **Notifications** | [Mako](https://github.com/emersion/mako) |

---

## 📁 Repository Structure

Package configurations mirror the home directory structure using **GNU Stow**:

```text
~/mingofiles/
├── fuzzel/      # App launcher settings
├── git/         # Global .gitconfig
├── kitty/       # Terminal styling and keybinds
├── mako/        # Notification daemon preferences
├── niri/        # Niri WM compositor configuration
├── nvim/        # Neovim init & plugin configs
├── swaylock/    # Screen locker setup
├── waybar/      # Status bar modules and CSS
├── zsh/         # Shell config (.zshrc, .p10k.zsh)
└── bootstrap.sh # Automated setup script
```

---

## 🚀 Quick Start & Installation

### Option A: Automatic Setup (Fresh Install)

Clone the repository and run the bootstrap script to install required system packages and set up all symlinks automatically:

```bash
git clone https://github.com/YOUR_USERNAME/mingofiles.git ~/mingofiles
cd ~/mingofiles
chmod +x bootstrap.sh
./bootstrap.sh
```

---

### Option B: Manual Setup

If you prefer to manage individual configurations manually:

1. **Install GNU Stow:**
   ```bash
   sudo pacman -S --needed stow
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mingofiles.git ~/mingofiles
   cd ~/mingofiles
   ```

3. **Stow specific packages:**
   ```bash
   # Symlink individual configurations
   stow niri
   stow waybar
   stow kitty
   stow zsh
   ```

To remove/unlink a package:
```bash
stow -D waybar
```

---

## ⚙️ Maintenance & Workflow

Since all configs are symlinked directly to `~/mingofiles`, any changes made inside `~/.config/` update this repository in real-time.

```bash
cd ~/mingofiles
git status
git add .
git commit -m "Update Waybar layout and Niri keybinds"
git push
```
