import streamlit as st
from datetime import date

# ----------------- VIEW RECORDS -----------------
def view_records(domain_name, df, filters=None):
    st.subheader(f"📄 {domain_name} Records")
    if df.empty:
        st.info("No data available.")
        return

    if filters:
        with st.expander("🔍 Filters"):
            selected_filters = {}
            for col, options in filters.items():
                selected_filters[col] = st.multiselect(col, options, default=options)
            for col, selected in selected_filters.items():
                df = df[df[col].isin(selected)]
    
    st.caption(f"Showing {len(df)} filtered records")
    st.dataframe(df, use_container_width=True)


# ----------------- ADD NEW RECORD -----------------
def add_new_record(domain_name, insert_func, form_fields):
    st.subheader(f"➕ Add New {domain_name} Record")
    with st.form(f"add_form_{domain_name}"):
        values = {}
        for field in form_fields:
            label = field["label"]
            ftype = field.get("type", "text")
            options = field.get("options")
            default = field.get("default", "")

            if ftype == "text":
                values[label] = st.text_input(label, value=default)
            elif ftype == "date":
                values[label] = st.date_input(label, value=default if default else date.today())
            elif ftype == "select":
                values[label] = st.selectbox(label, options)
            elif ftype == "textarea":
                values[label] = st.text_area(label, value=default)

        if st.form_submit_button("Save Record"):
            insert_func(**values)
            st.success(f"✔ {domain_name} record added successfully!")


# ----------------- UPDATE / DELETE -----------------
def update_delete_record(domain_name, df, update_func=None, delete_func=None, update_fields=None):
    st.subheader(f"✏ Update / Delete {domain_name} Record")
    if df.empty:
        st.warning("No records available.")
        return

    selected_id = st.selectbox("Select Record ID:", df["id"])
    selected_row = df[df["id"] == selected_id].iloc[0]
    st.json(selected_row.to_dict())

    if update_func and update_fields:
        updated_values = {}
        for field in update_fields:
            label = field["label"]
            options = field.get("options")
            if options:
                updated_values[label] = st.selectbox(f"Update {label}:", options)
            else:
                updated_values[label] = st.text_input(f"Update {label}:", value=selected_row[label])
        if st.button("Update Record"):
            update_func(selected_id, **updated_values)
            st.success("Record Updated Successfully!")

    if delete_func and st.button("❌ Delete Record"):
        delete_func(selected_id)
        st.error("Record Deleted!")
