"""
datasets.py - Provide helper functions for managing user in daabase
 - Function to retrive username
 - Function to add user to the database

"""

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

        cursor.execute(insert_sql, (
            dataset_name, source, category, last_updated,
            record_count, file_size_mb, created_at
        ))
        conn.commit()

        # return row count 
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


def get_top_recent_updates(conn):
    """
    Retrieve the 3 most recently updated datasets using pandas
    """
    # Load all data from the database
    df = pd.read_sql_query("SELECT * FROM dataset", conn)

   # Sort by last_updated descending and get top 3
    top3_recent_datasets = df.sort_values("last_updated", ascending=False).head(3)
  
    return top3_recent_datasets
