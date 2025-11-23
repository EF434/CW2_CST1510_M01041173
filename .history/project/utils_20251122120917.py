import streamlit as st
from datetime import date

def view_records(domain_name, df, filter_columns=None):
    """
    Display records for a domain with optional filtering.
    If filter_columns is provided, it automatically shows filter multiselects.
    """
    st.subheader(f"📄 {domain_name} Records")

    if df.empty:
        st.info("No data available.")
        return

    # Only create filters for columns that exist in the dataframe
    if filter_columns:
        filters = {col: df[col].unique() for col in filter_columns if col in df.columns}
        if filters:
            with st.expander("🔍 Filters"):
                for col, opts in filters.items():
                    selected = st.multiselect(col, opts, default=opts)
                    df = df[df[col].isin(selected)]  # Apply filters

    st.caption(f"Showing {len(df)} filtered records")
    st.dataframe(df, use_container_width=True)


def add_new_record(domain_name, insert_func, form_fields):
    st.subheader(f"➕ Add New {domain_name} Record")
    with st.form("add_form"):
        field_values = {}
        for field in form_fields:
            field_type = field.get("type", "text")
            label = field["label"]
            default = field.get("default")
            options = field.get
            ("options")
            
            if field_type == "text":
                field_values[label] = st.text_input(label, value=default or "")
            elif field_type == "date":
                field_values[label] = st.date_input(label, value=default or date.today())
            elif field_type == "select":
                field_values[label] = st.selectbox(label, options)
            elif field_type == "textarea":
                field_values[label] = st.text_area(label, value=default or "")

        if st.form_submit_button("Save Record"):
            insert_func(**field_values)
            st.success(f"✔ {domain_name} record added successfully!")

def update_delete_record(domain_name, df, update_func=None, delete_func=None, update_fields=None):
    st.subheader(f"✏ Update / Delete {domain_name} Record")
    if df.empty:
        st.warning("No records available.")
        return

    selected_id = st.selectbox("Select Record ID:", df["id"])
    selected_row = df[df["id"] == selected_id].iloc[0]
    st.write("📌 Existing Record:")
    st.json(selected_row.to_dict())

    if update_func and update_fields:
        field_values = {}
        for field in update_fields:
            label = field["label"]
            options = field.get("options")
            if options:
                field_values[label] = st.selectbox(f"Update {label}:", options)
            else:
                field_values[label] = st.text_input(f"Update {label}:", value=selected_row[label])

        if st.button("Update Record"):
            update_func(selected_id, **field_values)
            st.success("Record Updated Successfully!")

    if delete_func:
        if st.button("❌ Delete Record"):
            delete_func(selected_id)
            st.error("Record Deleted!")
