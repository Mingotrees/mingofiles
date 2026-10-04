# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=50
SAVEHIST=50
bindkey -v
# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename "$HOME/.zshrc"

autoload -Uz compinit
compinit
# End of lines added by compinstall
[[ ! -r /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme ]] || source /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

alias ctf='mv -i -- ~/Downloads/* "$PWD/"'
alias niriconf='vim ~/.config/niri/config.kdl'
alias kittyconf='vim ~/.config/kitty/kitty.conf'
alias waybarconf='vim ~/.config/waybar/config.jsonc'
alias waybarsconf='vim ~/.config/waybar/style.css'

[[ ! -r "$HOME/.local/bin/env" ]] || source "$HOME/.local/bin/env"


# Added by Antigravity CLI installer
export PATH="$HOME/.local/bin:$PATH"
#export PATH="$HOME/.docker-bin:$PATH"
