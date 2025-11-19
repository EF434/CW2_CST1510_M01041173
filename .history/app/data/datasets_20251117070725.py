# dataset.py

# Import required modules
import pandas as pd
import sqlite3


def insert_dataset(conn, dataset_name, source, category, last_updated,
                   record_count, file_size_mb, created_at=None):
    """
    Insert a new dataset entry into the database.

    Args:
        conn: Database connection
        dataset_name: TEXT NOT NULL
        category: TEXT (e.g., 'Threat Intelligence', 'Network Logs')
        source: TEXT (origin of the dataset)
        last_updated: TEXT (format: YYYY-MM-DD)
        record_count: INTEGER
        file_size_mb: REAL
        created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    Returns:
        int: ID of inserted record or None on failure
    """
    try:
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO dataset
        (dataset_name, source, category, last_updated, record_count, file_size_mb, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_sql, (dataset_name, source, category, last_updated,
            record_count, file_size_mb, created_at
        ))
        conn.commit()

        print(f"✅ Dataset '{dataset_name}' inserted successfully.")
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        print(f"⚠️ Dataset '{dataset_name}' already exists. Skipping...")
        return None

    except sqlite3.Error as e:
        print(f"❌ Error inserting dataset: {e}")
        return None



def get_all_datasets(conn):
    """
    Retrieve all dataset records.
    """
    try:
        df = pd.read_sql_query("SELECT * FROM dataset", conn)
        print(f"📄 Retrieved {len(df)} dataset entries.")
        return df
    except Exception as e:
        print(f"❌ Error retrieving datasets: {e}")
        return pd.DataFrame()



def update_dataset_record_count(conn, dataset_name, new_count):
    """
    Update the record_count field of a dataset.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE dataset SET record_count = ? WHERE dataset_name = ?",
            (new_count, dataset_name)
        )
        conn.commit()

        print(f"🔄 Dataset '{dataset_name}' record count updated to {new_count}.")
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Failed updating record count for '{dataset_name}': {e}")
        return 0



def delete_dataset(conn, dataset_name):
    """
    Delete a dataset entry.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM dataset WHERE dataset_name = ?",
            (dataset_name,)
        )
        conn.commit()

        print(f"🗑️ Dataset '{dataset_name}' deleted successfully.")
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Error deleting dataset '{dataset_name}': {e}")
        return 0



def get_dataset_summary(conn):
    """
    Return summary grouped by category.
    """
    query = """
    SELECT category, COUNT(*) AS dataset_count
    FROM dataset
    GROUP BY category
    ORDER BY dataset_count DESC
    """
    return pd.read_sql_query(query, conn)



def get_large_datasets(conn, min_size_mb=100):
    """
    Retrieve datasets larger than X MB.
    """
    query = f"""
    SELECT * FROM dataset
    WHERE file_size_mb >= {min_size_mb}
    ORDER BY file_size_mb DESC
    """
    return pd.read_sql_query(query, conn)
