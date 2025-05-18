# AI Agent Development Environment Guide
## Features
- Zephyr RTOS project management (init/clone/compile/test)
- PR switching and code review workflows
- Automated environment validation
- Cross-platform support (Windows/Linux/macOS)

## Environment Requirements
- Python 3.8+
- Git 2.20+
- CMake 3.20+
- West tool
- Supported boards: native_posix, qemu_x86, etc.

## Installation
```bash
pip install -r requirements.txt
```

## Usage Examples
### Zephyr Project Management
```bash
# Initialize development environment
python cli.py zephyr init --path ./my_project

# Clone Zephyr repository
python cli.py zephyr clone https://github.com/zephyrproject/your-repo.git

# Switch to specific PR
python cli.py zephyr pr 1234

# Compile project (native_posix board)
python cli.py zephyr compile -b native_posix

# Run Twister tests
python cli.py zephyr test -a "-p native_posix -T tests/kernel"
```

### Cody AI Assistant
```bash
# Single query mode
example-cli query "How to clean build cache"

# Interactive mode
example-cli interactive
```

## Support
Report issues at [GitHub Issues](https://github.com/your-repo/issues)