
# cmdfixer

An industry-grade CLI tool that suggests corrections for mistyped commands (git, Linux, Kubernetes, Docker, etc.).

## Features
- Fuzzy matching for command suggestions
- Extensible rule system
- Easy to add new commands
- Ready for PyPI publishing

## Installation
```sh
pip install cmdfixer
```

## Usage
```sh
cmdfixer <mistyped_command>
```

## Example
```
$ cmdfixer git sttaus
You entered: git sttaus
Suggested command: git status
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
MIT
