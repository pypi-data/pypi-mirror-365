# odoo_connector

A clean and lightweight Python connector for **Odoo's XML-RPC API**.

This package simplifies interactions with Odoo models using Python, so you can authenticate, read, create, update, and delete records easily.

## ✨ Features

- 🔐 Authentication via XML-RPC
- 📚 CRUD operations on any Odoo model
- 🔁 Generic method caller
- 🧼 Clean and well-documented code
- ✅ Ready for use in production or automation scripts

---

## 🛠️ Installation

### A. Clone the repository & install locally:

```bash
git clone https://github.com/your-user/odoo_connector.git
cd odoo_connector
pip install -e .
```

---

## 🚀 Usage

### 1. Import and initialize

```python
from odoo_connector import OdooConnector

odoo = OdooConnector(
    url='https://your-odoo-instance.com',
    db='your_database_name',
    username='admin@example.com',
    password='your_password'
)
```

### 2. Read records

```python
partners = odoo.read('res.partner', fields=['name', 'email'], limit=5)
for p in partners:
    print(p)
```

### 3. Create a record

```python
partner_id = odoo.create('res.partner', {
    'name': 'Bruce Wayne',
    'email': 'batman@gotham.com'
})
print("New Partner ID:", partner_id)
```

### 4. Update a record

```python
odoo.write('res.partner', [partner_id], {'phone': '+123456789'})
```

### 5. Delete a record

```python
odoo.unlink('res.partner', [partner_id])
```

### 6. Call a custom method

```python
has_rights = odoo.call_method(
    'res.partner',
    'check_access_rights',
    ['read'],
    {'raise_exception': False}
)
print("Has read access:", has_rights)
```

---

## 📦 Project Structure

```
odoo_connector/
├── odoo_connector/
│   ├── __init__.py
│   └── api.py
├── tests/
│   └── test_connector.py
├── setup.py
├── README.md
└── LICENSE
```
