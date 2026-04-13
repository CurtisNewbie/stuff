# Tmux Conf

```conf
set-option -g default-command "arch -arch arm64 /bin/bash"

set-option -g history-limit 10000
set -g default-terminal "screen-256color"
set-option -g renumber-windows on
set-window-option -g mode-keys vi
set-option -g status-interval 1
set-option -g automatic-rename on
set-option -g automatic-rename-format '#{b:pane_current_path}'

bind-key -T copy-mode-vi v send -X begin-selection
bind-key -T copy-mode-vi V send -X select-line
bind-key -T copy-mode-vi y send -X copy-pipe-and-cancel "pbcopy"

bind-key t swap-window -t 0
bind-key y swap-window -t 1

bind P paste-buffer

set -sg escape-time 0

bind c new-window -c "#{pane_current_path}"
bind '"' split-window -c "#{pane_current_path}"
bind % split-window -h -c "#{pane_current_path}"

# Layout: move current pane to left (main), stack others on right, widen left to 60%
# Usage: Ctrl+b Shift+L  (select the pane you want on the left first)
bind L run-shell "tmux swap-pane -s . -t 0 && tmux select-layout main-vertical && tmux resize-pane -t 0 -x 60%"

# set -g mouse on
# set -g default-terminal "screen-256color"
# set -ga terminal-overrides ',xterm-256color:smcup@:rmcup@'
# if-shell "[ $(uname) = Darwin ]" 'set -g terminal-overrides "xterm*:XT:smcup@:rmcup@"'
```

