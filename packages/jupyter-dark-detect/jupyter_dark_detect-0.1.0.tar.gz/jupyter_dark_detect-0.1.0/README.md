# jupyter-dark-detect

Detect dark mode in Jupyter environments (Notebook, Lab, VS Code, etc.).

## Installation

```bash
pip install jupyter-dark-detect
```

## Usage

```python
from jupyter_dark_detect import is_dark

# Check if Jupyter is running in dark mode
if is_dark():
    print("Dark mode is enabled!")
    # Use dark theme colors for visualizations
    bg_color = "#1e1e1e"
    text_color = "#d4d4d4"
else:
    print("Light mode is enabled!")
    # Use light theme colors for visualizations
    bg_color = "#ffffff"
    text_color = "#000000"
```

## Features

- **Multiple detection strategies** for maximum compatibility:
  - JupyterLab theme settings files
  - VS Code workspace and user settings
  - JavaScript-based DOM inspection
  - System preferences (macOS and Windows)
  
- **Zero configuration** - just import and use

- **Lightweight** with minimal dependencies (only requires IPython)

- **Cross-platform** support for JupyterLab, Jupyter Notebook, VS Code, and more

## How It Works

The package tries multiple detection methods in order:

1. **JupyterLab Settings**: Checks `~/.jupyter/lab/user-settings/` for theme configuration
2. **VS Code Settings**: When running in VS Code, checks both workspace and user settings
3. **JavaScript Detection**: Uses IPython magic to inspect the DOM for theme classes
4. **System Preferences**: Falls back to OS-level dark mode settings on macOS and Windows

## Use Cases

- **Matplotlib/Plotly Visualizations**: Automatically adjust plot colors based on theme
- **Rich Terminal Output**: Style console output to match the notebook theme
- **Custom Widgets**: Build theme-aware Jupyter widgets
- **Documentation**: Generate screenshots that match the user's theme

## Example: Matplotlib Integration

```python
import matplotlib.pyplot as plt
from jupyter_dark_detect import is_dark

# Set style based on theme
plt.style.use('dark_background' if is_dark() else 'default')

# Your plotting code
plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
plt.title("Theme-Aware Plot")
plt.show()
```

## Example: Plotly Integration

```python
import plotly.graph_objects as go
from jupyter_dark_detect import is_dark

# Create theme-aware Plotly figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 4, 9, 16]))

# Update layout based on theme
if is_dark():
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e"
    )
else:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

fig.show()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.