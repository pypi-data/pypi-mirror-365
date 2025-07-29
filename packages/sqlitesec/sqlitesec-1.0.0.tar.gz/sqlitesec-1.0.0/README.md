# SqliteSec

**Secure SQLite databases with AES-256 encryption**

SqliteSec protects your SQLite databases by encrypting them with industry-standard AES-256 encryption. Share sensitive data safely or work with confidential information without compromising security.

## Installation

```bash
pip install sqlitesec
```

## Features

- **AES-256 encryption** - Military-grade security for your databases
- **Seamless integration** - Drop-in replacement for standard SQLite connections
- **Automatic encryption/decryption** - Transparent operation with your existing code
- **Secure file sharing** - Safely send encrypted databases to others

## Quick Start

```python
from sqlitesec import SqliteSec
import os

# Initialize with your encryption key
key = os.urandom(32)  # Generate a secure 256-bit key
sqs = SqliteSec(key)

# Create and use encrypted database
conn = sqs.connect("secure.db")
cursor = conn.cursor()

# Standard SQLite operations work normally
cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
cursor.execute('INSERT INTO users (name) VALUES (?)', ('Alice',))
conn.commit()

# Always close properly to ensure encryption
sqs.close(conn, "secure.db")
```

## Reading Encrypted Data

```python
# Reconnect and read data
conn = sqs.connect("secure.db")
cursor = conn.cursor()

cursor.execute('SELECT name FROM users WHERE id = 1')
user_name = cursor.fetchone()[0]
print(f"User: {user_name}")

sqs.close(conn, "secure.db")
```

## API Reference

### `SqliteSec(key)`
Initialize with encryption key (32 bytes for AES-256).

### `connect(database_path)`
Open encrypted database connection. Returns standard SQLite connection object.

### `close(connection, database_path)`
Properly close connection and ensure data is encrypted.

---

**Security Note**: Always use a strong, randomly generated key and store it securely.
