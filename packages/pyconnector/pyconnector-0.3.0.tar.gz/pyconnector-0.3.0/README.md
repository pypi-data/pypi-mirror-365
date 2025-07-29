# 🔌 pyconnector

**pyconnector** is a flexible, pluggable Python package designed to connect seamlessly to popular databases and services including Databricks, PostgreSQL, SMTP, and SFTP — using JDBC, ODBC, or native protocols.

# Structure
.
|-- LICENSE
|-- README.md
|-- build.sh
|-- docs
|   |-- google.md
|   `-- pyconnector.md
|-- pyconnector
|   |-- core
|   |   |-- base_db_connector.py
|   |   `-- base_google_connector.py
|   |-- databricks
|   |   |-- __init__.py
|   |   |-- api_connector.py
|   |   |-- jdbc_connector.py
|   |   |-- odbc_connector.py
|   |   `-- sql_connector.py
|   |-- driver_utils.py
|   |-- mysql
|   |   |-- __init__.py
|   |   `-- connector.py
|   |-- postgres
|   |   |-- __init__.py
|   |   |-- api_connector.py
|   |   |-- connector.py
|   |   |-- jdbc_connector.py
|   |   `-- odbc_connector.py
|   |-- pygoogle
|   |   |-- __init__.py
|   |   |-- api_connector.py
|   |   |-- drive_connector.py
|   |   `-- gmail_connector.py
|   |-- sftp
|   |   |-- __init__.py
|   |   `-- basic_connector.py
|   |-- sharepoint
|   |   |-- __init__.py
|   |   `-- api_connector.py
|   `-- smtp
|       |-- __init__.py
|       `-- basic_connector.py
|-- pyproject.toml
|-- requirements.txt
|-- setup.cfg
|-- token.pickle
`-- token_gmail.pickle

11 directories, 35 files


## ✨ Features

- ✅ Multi-system support: Databricks, Postgres, SMTP, SFTP  
- 🔄 Multi-mode: JDBC and ODBC connectors  
- ⚙️ Dynamic driver versioning and loading  
- 📦 Lightweight, modular, and extensible  
- 🧩 Easy to plug in new systems  

## 📦 Installation

```bash
pip install pyconnector


# 🔌 Included Connectors
Databricks
google - Gmail, Drive
MySql
Postgres

JDBC API, SQL. JDBc. ODBC Connector 

ODBC Connector

PostgreSQL

JDBC Connector

ODBC Connector

SMTP

Basic email sending support

SFTP

File upload/download over SSH

SHAREPOINT API Connector


#  Driver Management
All JDBC/ODBC drivers are stored in the local /drivers directory and loaded dynamically by:

system (e.g., databricks, postgres)

driver_type (jdbc or odbc)

version (optional; defaults to latest)