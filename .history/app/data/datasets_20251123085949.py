"""
datasets.py - Provide helper functions for managing user in daabase
 - Function to retrive username
 - Function to add user to the database

"""

# Import required modules
import pandas as pd
import sqlite3

# 🌟 Add a new dataset
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
        INSERT INTO datasets_metadata
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

# 🌟 Retrieve all datasets from the database 
def get_all_datasets(conn):
    """
    Get all datasets from the database.
    
    TODO: Implement using pandas.read_sql_query()
    
    Returns:
        pandas.DataFrame: All incidents
    """
    # TODO: Use pd.read_sql_query("SELECT * FROM datasets", conn)
    try:
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
        print(f"✅ Retrieved {len(df)} datasets from the database.")
        return df
    except Exception as e:
        print(f"Error retrieving datasets: {e}")
        return pd.DataFrame()
    
# 🌟 Update the record count
def update_dataset(conn, dataset_name, new_count):
    """
    Update the record_count field of a dataset.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE datasets_metadata SET record_count = ? WHERE dataset_name = ?",
            (new_count, dataset_name)
        )
        conn.commit()

        print(f"🔄 Dataset '{dataset_name}' record count updated to {new_count}.")
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Failed updating record count for '{dataset_name}': {e}")
        return 0


# 🌟 Delete a dataset
def delete_dataset(conn, dataset_name):
    """
    Delete a dataset entry.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM datasets_metadata WHERE dataset_name = ?",
            (dataset_name,)
        )
        conn.commit()

        print(f"🗑️ Dataset '{dataset_name}' deleted successfully.")
        return cursor.rowcount

    except Exception as e:
        print(f"❌ Error deleting dataset '{dataset_name}': {e}")
        return 0

# 📊 Get 3 most recently updated datasets
def get_top_recent_updates(conn):
    """
    Retrieve the 3 most recently updated datasets using pandas
    """
    # Load all data from the database
    df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)

    # Sort by last_updated descending and get top 3
    top3_recent_datasets = df.sort_values("last_updated", ascending=False).head(3)
  
    return top3_recent_datasets

# 📊 Check dataset resource usage
def display_resource_usage(conn):
    """
    Check which datasets use the most storage or have the most rows.
    """

    insert_sql = """
    SELECT dataset_name, record_count, file_size_mb
    FROM datasets_metadata
    ORDER BY file_size_mb DESC, record_count DESC
    """
    df = pd.read_sql_query(insert_sql, conn)
    return df

# 📊 Analyze source dependency
def list_datasets_by_source(conn):
    """
     Count datasets grouped by source to see which sources contribute the most.
    """
    insert_sql = """
        SELECT source, COUNT(*) AS dataset_count
        FROM datasets_metadata
        GROUP BY source
        ORDER BY dataset_count DESC
    """

    df = pd.read_sql_query(insert_sql, conn)
    return df

# ------------------- DATA VISUALIZATION FOR DATASETS -------------------
def data_visualization(conn, table_name):
    if table_name != "datasets_metadata":
        st.info("Visualizations are only implemented for Data Science datasets for now.")
        return

    st.subheader("📊 Data Science Datasets Visualizations")

    # ---------- LOAD DATA ----------
    df_all = get_all_datasets(conn)
    if df_all.empty:
        st.info("No dataset metadata available for visualization.")
        return

    # ---------- FILTERS ----------
    category_filter = st.multiselect(
        "Select Category",
        options=df_all["category"].unique(),
        default=df_all["category"].unique()
    )

    filtered_df = df_all[df_all["category"].isin(category_filter)]
    st.caption(f"Showing {len(filtered_df)} datasets after filtering.")

    # ---------- LAYOUT ----------
    col1, col2 = st.columns(2)

    # 1️⃣ Top 3 Most Recently Updated Datasets
    with col1:
        st.subheader("Top 3 Recently Updated Datasets")
        top3 = get_top_recent_updates(conn)
        if not top3.empty:
            fig1 = px.bar(top3, x="dataset_name", y="last_updated",
                          color="category", title="Top 3 Recently Updated Datasets")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No datasets found.")

    # 2️⃣ Resource Usage: Storage and Record Count
    with col2:
        st.subheader("Resource Usage")
        df_resource = display_resource_usage(conn)
        if not df_resource.empty:
            fig2 = px.bar(df_resource, x="dataset_name", y=["file_size_mb", "record_count"],
                          barmode="group", title="Dataset Storage and Record Count")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No dataset resource info found.")

    # 3️⃣ Dataset Count by Source
    st.subheader("Datasets by Source")
    df_source = list_datasets_by_source(conn)
    if not df_source.empty:
        fig3 = px.pie(df_source, names="source", values="dataset_count",
                      title="Dataset Count by Source")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No dataset sources found.")

    # ---------- RAW DATA EXPANDER ----------
    with st.expander("See Filtered Dataset Metadata"):
        st.dataframe(filtered_df, use_container_width=True)
