# CSS Tidy

A Python tool to tidy and format CSS files.

## Features

- **CSS Formatting**: Automatically format CSS code to make it more readable
- **Syntax Validation**: Check CSS syntax errors
- **Batch Processing**: Support batch processing of multiple CSS files
- **Custom Options**: Customize indentation, line breaks, and other formatting options
- **Selector Grouping**: Automatically group related CSS selectors by prefix
- **Command Line Tool**: Provide simple and easy-to-use command line interface

## Installation

```bash
pip install css-tidy
```

## Usage
```
css-tidy [css-file-name] [options]
```

### Command Line Usage

```bash
# Format a single CSS file
css-tidy style.css

# Format and output to a new file
css-tidy input.css -o output.css

# Batch process all CSS files in a directory
css-tidy *.css

# Use custom indentation
css-tidy style.css --indent 4

# Minify CSS
css-tidy style.css --minify

# Group selectors
css-tidy style.css --group
```

## Command Line Options

```
Usage: css-tidy [OPTIONS] INPUT_FILE

Options:
  -o, --output TEXT          Output file path
  -i, --indent INTEGER       Indentation size (default: 2)
  -m, --minify              Minify CSS output
  -s, --sort                Sort CSS properties
  -c, --remove-comments     Remove CSS comments
  -g, --group               Group CSS selectors by prefix
  -v, --verbose             Enable verbose output
  --validate-only           Only validate CSS, do not format
  --version                 Show version and exit
  --help                    Show this message and exit
```

### Python API Usage

```python
from css_tidy import CSSFormatter

# Create formatter
formatter = CSSFormatter()

# Format CSS string
css_code = """
body{margin:0;padding:0}div{color:red}
"""
formatted_css = formatter.format(css_code)
print(formatted_css)

# Format file
formatter.format_file('input.css', 'output.css')

# Use custom options
formatter = CSSFormatter(indent_size=4, max_line_length=80)
formatted_css = formatter.format(css_code)

# Group selectors
formatter = CSSFormatter(group_selectors=True)
formatted_css = formatter.format(css_code)
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

If you have questions or need help, please open an issue on GitHub.

Thank you to all contributors and the open-source community for your support.