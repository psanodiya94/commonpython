# Installation Guide

This guide provides detailed installation instructions for the CommonPython framework, clearly indicating which dependencies are mandatory versus optional.

## 📋 Dependency Overview

| Category | Status | Purpose |
|----------|--------|---------|
| **Core Framework** | ✅ Mandatory | Basic framework functionality |
| **CLI Tools** | ⚙️ Optional | For CLI-based database/messaging |
| **Library Packages** | 🚀 Optional | For high-performance operations |
| **Development Tools** | 🧪 Optional | For testing and development |

---

## ✅ Step 1: Mandatory Installation (Required)

These dependencies are **always required** for the framework to function.

### Install Framework

```bash
# Clone the repository
git clone https://github.com/your-org/commonpython.git
cd commonpython

# Install with mandatory dependencies only
pip install -e .
```

This installs:
- ✅ Python 3.8+ (runtime)
- ✅ PyYAML (configuration parsing)

**Minimum viable installation** - The framework will work but you'll need either CLI tools or library packages for actual database/messaging operations.

---

## ⚙️ Step 2: CLI Implementation (Optional)

Install these if you want to use **CLI-based implementations** (default).

### For Database Operations

**Install IBM DB2 CLI Tools:**

```bash
# On Linux (Ubuntu/Debian)
wget https://public.dhe.ibm.com/ibmdl/export/pub/software/data/db2/drivers/odbc_cli/linuxx64_odbc_cli.tar.gz
tar -xvf linuxx64_odbc_cli.tar.gz
cd odbc_cli
sudo ./db2_install

# Add to PATH
export PATH=$PATH:/opt/ibm/db2/V11.5/bin
```

**Verify installation:**
```bash
db2 -v
# Should display DB2 CLI version
```

### For Messaging Operations

**Install IBM MQ CLI Tools:**

```bash
# On Linux (Ubuntu/Debian)
wget https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/messaging/mqdev/redist/9.3.0.0-IBM-MQC-Redist-LinuxX64.tar.gz
tar -xvf 9.3.0.0-IBM-MQC-Redist-LinuxX64.tar.gz
cd MQServer
sudo ./mqlicense.sh -accept
sudo rpm -ivh MQSeriesRuntime-*.rpm MQSeriesClient-*.rpm

# Add to PATH
export PATH=$PATH:/opt/mqm/bin
```

**Verify installation:**
```bash
dspmqver
# Should display IBM MQ version
```

> 💡 **Note**: Only install CLI tools if you plan to use CLI implementation. You can skip this if using library implementations.

---

## 🚀 Step 3: Library Implementation (Optional - Recommended)

Install these for **10-50x better performance** with native Python libraries.

### Option A: Install All Library Dependencies

```bash
# Install all library adapters (recommended)
pip install -e ".[library]"
```

This installs:
- 🚀 ibm_db >= 3.0.0 (native DB2 operations)
- 🚀 pymqi >= 1.12.0 (native MQ operations)

### Option B: Install Selectively

**Database library only:**
```bash
pip install -e ".[db-library]"
# Installs: ibm_db >= 3.0.0
```

**Messaging library only:**
```bash
pip install -e ".[mq-library]"
# Installs: pymqi >= 1.12.0
```

**Verify installation:**
```bash
python -c "import ibm_db; print('ibm_db installed')"
python -c "import pymqi; print('pymqi installed')"
```

> 💡 **Note**: Library implementations are **optional**. The framework auto-falls back to CLI if not installed.

---

## 🧪 Step 4: Development Dependencies (Optional)

Install these if you're **developing or testing** the framework.

### For Testing

```bash
# Install test dependencies
pip install -e ".[test]"
```

This installs:
- 🧪 coverage >= 7.0.0 (code coverage analysis)

### For Development

```bash
# Install development dependencies
pip install -e ".[dev]"
```

This installs:
- 🧪 coverage >= 7.0.0 (code coverage)

### Install Everything

```bash
# Install all dependencies (mandatory + all optional)
pip install -e ".[all]"
```

This installs:
- ✅ PyYAML (mandatory)
- 🚀 ibm_db >= 3.0.0 (optional library)
- 🚀 pymqi >= 1.12.0 (optional library)
- 🧪 coverage >= 7.0.0 (optional testing)

---

## 📊 Installation Scenarios

### Scenario 1: Minimal Installation (CLI-based)

```bash
# Install framework only
pip install -e .

# Install IBM CLI tools separately (see Step 2)
# Configure for CLI implementation (default)
```

**Use case**: Quick setup, existing CLI tools infrastructure

### Scenario 2: High-Performance Setup (Library-based)

```bash
# Install framework with library adapters
pip install -e ".[library]"

# Configure for library implementation
```

**Use case**: Production deployments, performance-critical applications

### Scenario 3: Development Setup (Full)

```bash
# Install everything
pip install -e ".[all]"

# Run tests
python scripts/test_commonpython.py --coverage
```

**Use case**: Framework development, testing both implementations

### Scenario 4: Database-Only Setup

```bash
# Install framework with DB library
pip install -e ".[db-library]"

# Configure database for library implementation
# Messaging will use CLI (if tools installed) or error if not
```

**Use case**: Database-only applications

---

## ✅ Verification

### Check What's Installed

```bash
# Check adapter availability
python -c "
from commonpython.factories import ManagerFactory
available = ManagerFactory.get_available_implementations()
print('Database - CLI:', available['database']['cli'])
print('Database - Library:', available['database']['library'])
print('Messaging - CLI:', available['messaging']['cli'])
print('Messaging - Library:', available['messaging']['library'])
"
```

### Run Tests

```bash
# Run test suite to verify installation
python scripts/test_commonpython.py

# Run with coverage (if installed)
python scripts/test_commonpython.py --coverage
```

### Check Specific Components

```bash
# Test database connectivity
python -c "
from commonpython.config import ConfigManager
from commonpython.factories import ManagerFactory

config = ConfigManager('config/config.yaml')
db_config = config.get_database_config()
db_manager = ManagerFactory.create_database_manager(db_config)
print('Database manager created:', type(db_manager).__name__)
"
```

---

## 🔧 Configuration

After installation, configure the framework to use your preferred implementation:

### For CLI Implementation (Default)

```yaml
# config/config.yaml
database:
  implementation: cli  # Use CLI tools
  auto_fallback: true
  # ... connection details

messaging:
  implementation: cli  # Use CLI tools
  auto_fallback: true
  # ... connection details
```

### For Library Implementation

```yaml
# config/config.yaml
database:
  implementation: library  # Use ibm_db
  auto_fallback: true      # Fallback to CLI if library unavailable
  # ... connection details

messaging:
  implementation: library  # Use pymqi
  auto_fallback: true      # Fallback to CLI if library unavailable
  # ... connection details
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'ibm_db'"

**Cause**: Library implementation requested but ibm_db not installed.

**Solutions**:
1. Install library: `pip install ibm_db`
2. Enable auto-fallback in config: `auto_fallback: true`
3. Switch to CLI: `implementation: cli`

### "ModuleNotFoundError: No module named 'pymqi'"

**Cause**: Library implementation requested but pymqi not installed.

**Solutions**:
1. Install library: `pip install pymqi`
2. Enable auto-fallback in config: `auto_fallback: true`
3. Switch to CLI: `implementation: cli`

### "DB2 command not found"

**Cause**: CLI implementation requested but DB2 CLI tools not in PATH.

**Solutions**:
1. Install DB2 CLI tools (see Step 2)
2. Add to PATH: `export PATH=$PATH:/opt/ibm/db2/V11.5/bin`
3. Switch to library: `implementation: library` (if ibm_db installed)

### "MQ command not found"

**Cause**: CLI implementation requested but MQ CLI tools not in PATH.

**Solutions**:
1. Install MQ CLI tools (see Step 2)
2. Add to PATH: `export PATH=$PATH:/opt/mqm/bin`
3. Switch to library: `implementation: library` (if pymqi installed)

---

## 📚 Next Steps

After installation:

1. **Read the Architecture Guide**: [docs/ADAPTER_ARCHITECTURE.md](docs/ADAPTER_ARCHITECTURE.md)
2. **Try the Quick Start**: [examples/quick_start.py](examples/quick_start.py)
3. **Review Configuration**: [config/config.yaml](config/config.yaml)
4. **Run Tests**: `python scripts/test_commonpython.py`
5. **Build Your First Component**: Copy [examples/component_template.py](examples/component_template.py)

---

## 💡 Recommendations

| Scenario | Recommended Installation |
|----------|-------------------------|
| **Production** | `pip install -e ".[library]"` - Best performance |
| **Development** | `pip install -e ".[all]"` - Full testing capability |
| **Quick Testing** | `pip install -e .` - Minimal setup |
| **CI/CD** | `pip install -e ".[test]"` - Testing only |
| **Legacy Systems** | `pip install -e .` + CLI tools - Existing infrastructure |

---

## 📞 Support

For installation issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review test output: `python scripts/test_commonpython.py`
3. Check adapter availability (see [Verification](#verification))
4. Consult [ADAPTER_ARCHITECTURE.md](docs/ADAPTER_ARCHITECTURE.md)
