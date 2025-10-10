# Tmux Conf

```
set-option -g default-command "arch -arch arm64 /bin/bash"

set-option -g history-limit 4000
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

bind P paste-buffer

set -sg escape-time 0

bind c new-window -c "#{pane_current_path}"
bind '"' split-window -c "#{pane_current_path}"
bind % split-window -h -c "#{pane_current_path}"
```

