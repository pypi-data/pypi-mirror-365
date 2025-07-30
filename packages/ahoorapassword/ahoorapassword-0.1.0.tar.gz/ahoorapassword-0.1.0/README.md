# ahoorapassword

A simple and colorful password generator written in Python.  
It supports numeric or full-character passwords and automatically copies the result to the clipboard.

## Features
- Generate passwords using digits or full characters
- Auto copy to clipboard
- Colorful output using `colorama`

## Installation

```
pip install ahoorapassword
```

## Usage

```python
from ahoorapassword import password_new

# Default (12 random characters)
password_new()

# Only numbers
password_new(10, typepass="number")
```

## License

MIT License