# CW2_CST1510_M01041173

# Week 8: Data Pipeline & CRUD (SQL)
Student Name: Emaan Fatima  
Student ID: M01041173  
Course: CST1510 - CW2 - Multi-Domain Intelligence Platform

## Project Description
This project upgrades the Week 7 file-based authentication system by integrating a **SQLite database** to store and manage user, incident, dataset, and IT ticket information. The system now supports **CRUD operations**, efficient CSV data loading, and secure query execution. Users can interact with the database to create, read, update, and delete records across multiple domains, enabling real-world data management capabilities.

## Features
- Migration of Week 7 users from `users.txt` → SQLite database
- Database tables for multiple domains: `cyber_incidents`, `datasets_metadata`, `it_tickets`
- CSV data loading using pandas for bulk data import
- Full CRUD operations:
  - **Create:** Insert new users, incidents, datasets, or tickets
  - **Read:** Retrieve records and query insights
  - **Update:** Modify existing records securely
  - **Delete:** Remove unwanted records
- Parameterized queries to prevent SQL injection
- Persistent data storage with SQLite database
- Query testing with real-world scenarios

## Technical Implementation
- **Database:** SQLite3
- **Data Loading:** pandas for CSV import
- **CRUD Functions:** Python functions with `sqlite3` parameterized queries
- **Security:** SQL injection prevention using parameterized queries
- **Table Structure:**
  - `users` — stores user credentials and roles
  - `cyber_incidents` — logs security incidents
  - `datasets_metadata` — stores metadata of datasets
  - `it_tickets` — manages IT support tickets
- **Persistence:** Data stored in `intelligence_platform.db` with folder structure `DATA/`
- **Python Modules Used:** `sqlite3`, `pandas`, `pathlib`

## Beginner Tip
Think of a database like a **super-powered Excel file** that:
- Lives on disk (persists data)
- Lets you search, add, update, and delete data **without reading the whole file**
- Can link related data together (users → incidents)
- Protects against data corruption
