# Tmux Conf

```
set -g default-terminal "screen-256color"
set-option -g renumber-windows on
set-window-option -g mode-keys vi
bind-key -T copy-mode-vi v send -X begin-selection
bind-key -T copy-mode-vi V send -X select-line
```

