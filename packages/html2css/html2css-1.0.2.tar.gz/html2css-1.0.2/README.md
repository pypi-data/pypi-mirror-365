# 🛠 html2css

A simple Python CLI tool that automatically generates a CSS skeleton (`style.css`) from an HTML file.  
No need to manually type selectors — just run a command and let it do the work for you.

## update(v1.0.1)
    -nth-child selector support: Now correctly applies :nth-child(n) to repeated HTML tags that do not have unique id or class attributes.
    -Handles repeated ids and classes gracefully with appropriate structural nesting.
    -Introduced ^= (starts-with) selector handling for dynamic or pattern-based attribute detection.
    
## 🚀 Features

- Detects HTML tags, IDs, and class names
- Outputs a starter `style.css` with all selectors structured
- Includes responsive media queries
- Works globally via the `html2css` command


## 📦 Installation (after publishing to PyPI)

```bash
pip install --upgrade html2css
