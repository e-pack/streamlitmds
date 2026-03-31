import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Snowflake MDM Workbench", page_icon="❄️", layout="wide")

# -----------------------------
# Seed data
# -----------------------------
if "master_data" not in st.session_state:
    st.session_state.master_data = pd.DataFrame([
        {
            "Customer_ID": "CUST-1001",
            "Customer_Name": "Acme Health",
            "Domain": "Customer",
            "Status": "Approved",
            "Country": "US",
            "Region": "NA",
            "Parent_Customer_ID": "",
            "Tax_ID": "98-7654321",
            "Effective_From": "2026-01-01",
            "Effective_To": "",
            "Published_Version": "v1.2",
            "Last_Changed_By": "data.steward",
            "Last_Changed_At": "2026-03-27 10:15"
        },
        {
            "Customer_ID": "CUST-1002",
            "Customer_Name": "Northwind Retail",
            "Domain": "Customer",
            "Status": "Pending Approval",
            "Country": "CA",
            "Region": "NA",
            "Parent_Customer_ID": "CUST-1001",
            "Tax_ID": "CA-112233",
            "Effective_From": "2026-03-01",
            "Effective_To": "",
            "Published_Version": "Draft",
            "Last_Changed_By": "business.user",
            "Last_Changed_At": "2026-03-30 16:40"
        },
        {
            "Product_ID": "PRD-2001",
            "Product_Name": "Premium Support",
            "Domain": "Product",
            "Status": "Approved",
            "Category": "Services",
            "Is_Active": True,
            "GL_Code": "4100",
            "Effective_From": "2026-01-15",
            "Effective_To": "",
            "Published_Version": "v2.0",
            "Last_Changed_By": "mdm.admin",
            "Last_Changed_At": "2026-03-29 09:10"
        }
    ])

if "change_requests" not in st.session_state:
    st.session_state.change_requests = pd.DataFrame([
        {
            "CR_ID": "CR-501",
            "Domain": "Customer",
            "Entity_Key": "CUST-1002",
            "Change_Type": "Create",
            "Requested_By": "business.user",
            "Approver": "data.owner",
            "Status": "Pending Approval",
            "Submitted_At": "2026-03-30 16:42",
            "Environment": "Dev"
        },
        {
            "CR_ID": "CR-502",
            "Domain": "Product",
            "Entity_Key": "PRD-2001",
            "Change_Type": "Update",
            "Requested_By": "data.steward",
            "Approver": "finance.owner",
            "Status": "Approved",
            "Submitted_At": "2026-03-29 09:15",
            "Environment": "Prod"
        }
    ])

if "release_log" not in st.session_state:
    st.session_state.release_log = pd.DataFrame([
        {"Release": "v2.0", "Environment": "Prod", "Domain": "Product", "Published_By": "mdm.admin", "Published_At": "2026-03-29 10:00", "Notes": "Quarterly curated product publish"},
        {"Release": "v1.2", "Environment": "Prod", "Domain": "Customer", "Published_By": "data.owner", "Published_At": "2026-03-27 11:30", "Notes": "Approved customer hierarchy refresh"},
    ])

SCHEMAS = {
    "Customer": {
        "columns": [
            "Customer_ID", "Customer_Name", "Country", "Region", "Parent_Customer_ID",
            "Tax_ID", "Effective_From", "Effective_To"
        ],
        "required": ["Customer_ID", "Customer_Name", "Country", "Effective_From"],
        "types": {
            "Customer_ID": "TEXT", "Customer_Name": "TEXT", "Country": "TEXT",
            "Region": "TEXT", "Parent_Customer_ID": "RELATIONSHIP", "Tax_ID": "TEXT",
            "Effective_From": "DATE", "Effective_To": "DATE"
        },
        "relationships": ["Parent_Customer_ID -> Customer.Customer_ID (self-reference hierarchy)"]
    },
    "Product": {
        "columns": [
            "Product_ID", "Product_Name", "Category", "Is_Active", "GL_Code",
            "Effective_From", "Effective_To"
        ],
        "required": ["Product_ID", "Product_Name", "Category", "Effective_From"],
        "types": {
            "Product_ID": "TEXT", "Product_Name": "TEXT", "Category": "TEXT",
            "Is_Active": "BOOLEAN", "GL_Code": "TEXT", "Effective_From": "DATE", "Effective_To": "DATE"
        },
        "relationships": []
    }
}

RULES = {
    "Customer": [
        "Customer_ID must be unique",
        "Customer_Name is required",
        "Country must be one of: US, CA, UK, DE, IN",
        "Effective_To cannot be before Effective_From",
        "Parent_Customer_ID must reference an existing Customer_ID if populated"
    ],
    "Product": [
        "Product_ID must be unique",
        "Product_Name is required",
        "Category is required",
        "Effective_To cannot be before Effective_From"
    ]
}

COUNTRY_VALUES = ["US", "CA", "UK", "DE", "IN"]
ROLE = st.sidebar.selectbox("Role", ["Business User", "Data Steward", "Approver", "MDM Admin"])
ENV = st.sidebar.radio("Target Environment", ["Dev", "Prod"], horizontal=True)
DOMAIN = st.sidebar.selectbox("Master Data Domain", ["Customer", "Product"])
page = st.sidebar.radio(
    "Navigation",
    [
        "Workbench",
        "Change Requests",
        "Data Quality",
        "Metadata",
        "Access & Governance",
        "Publish / Versioning",
        "Snowflake Landing"
    ]
)

st.title("❄️ Snowflake MDM Workbench")
st.caption("Mock app focused on Excel-like stewardship, rules, approvals, publication, and Snowflake delivery.")

# -----------------------------
# Helper functions
# -----------------------------
def domain_frame(domain: str) -> pd.DataFrame:
    df = st.session_state.master_data.copy()
    if domain == "Customer":
        cols = [c for c in ["Customer_ID", "Customer_Name", "Domain", "Status", "Country", "Region", "Parent_Customer_ID", "Tax_ID", "Effective_From", "Effective_To", "Published_Version", "Last_Changed_By", "Last_Changed_At"] if c in df.columns]
    else:
        cols = [c for c in ["Product_ID", "Product_Name", "Domain", "Status", "Category", "Is_Active", "GL_Code", "Effective_From", "Effective_To", "Published_Version", "Last_Changed_By", "Last_Changed_At"] if c in df.columns]
    filtered = df[df["Domain"] == domain] if "Domain" in df.columns else df
    return filtered[cols].fillna("")


def validate(df: pd.DataFrame, domain: str):
    issues = []
    schema = SCHEMAS[domain]

    # required checks
    for req in schema["required"]:
        if req in df.columns:
            missing = df[df[req].astype(str).str.strip() == ""]
            for idx in missing.index:
                issues.append({"Row": idx + 1, "Column": req, "Severity": "Error", "Issue": f"{req} is required"})

    # uniqueness
    key_col = "Customer_ID" if domain == "Customer" else "Product_ID"
    if key_col in df.columns:
        duplicates = df[df[key_col].astype(str).str.strip() != ""][df[key_col].duplicated(keep=False)]
        for idx in duplicates.index:
            issues.append({"Row": idx + 1, "Column": key_col, "Severity": "Error", "Issue": f"Duplicate {key_col}"})

    # date validation
    if set(["Effective_From", "Effective_To"]).issubset(df.columns):
        for idx, row in df.iterrows():
            ef = str(row.get("Effective_From", "")).strip()
            et = str(row.get("Effective_To", "")).strip()
            try:
                ef_dt = pd.to_datetime(ef) if ef else None
                et_dt = pd.to_datetime(et) if et else None
                if ef_dt is not None and et_dt is not None and et_dt < ef_dt:
                    issues.append({"Row": idx + 1, "Column": "Effective_To", "Severity": "Error", "Issue": "Effective_To cannot be before Effective_From"})
            except Exception:
                issues.append({"Row": idx + 1, "Column": "Effective_From / Effective_To", "Severity": "Error", "Issue": "Invalid date format"})

    # domain-specific
    if domain == "Customer":
        if "Country" in df.columns:
            invalid_country = df[(df["Country"].astype(str).str.strip() != "") & (~df["Country"].isin(COUNTRY_VALUES))]
            for idx in invalid_country.index:
                issues.append({"Row": idx + 1, "Column": "Country", "Severity": "Error", "Issue": "Country outside allowed list"})

        if set(["Parent_Customer_ID", "Customer_ID"]).issubset(df.columns):
            ids = set(df["Customer_ID"].astype(str).tolist())
            for idx, row in df.iterrows():
                parent = str(row.get("Parent_Customer_ID", "")).strip()
                if parent and parent not in ids:
                    issues.append({"Row": idx + 1, "Column": "Parent_Customer_ID", "Severity": "Error", "Issue": "Parent_Customer_ID does not exist in Customer_ID"})

    return pd.DataFrame(issues)


# -----------------------------
# Summary header
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Environment", ENV)
col2.metric("Role", ROLE)
col3.metric("Pending Approvals", int((st.session_state.change_requests["Status"] == "Pending Approval").sum()))
col4.metric("Published Releases", len(st.session_state.release_log))

# -----------------------------
# Workbench page
# -----------------------------
if page == "Workbench":
    st.subheader(f"{DOMAIN} Workbench")
    st.write("Business-friendly grid editing with fixed metadata-driven columns. Users can edit values, but they cannot add new columns.")

    schema_cols = SCHEMAS[DOMAIN]["columns"]
    df = domain_frame(DOMAIN)
    editable_df = df.copy()

    st.info("Column structure is locked by metadata policy. This mock enforces the important requirement: users cannot add a new column.")

    if DOMAIN == "Customer":
        column_config = {
            "Customer_ID": st.column_config.TextColumn(disabled=True, help="System-defined business key"),
            "Customer_Name": st.column_config.TextColumn(required=True),
            "Country": st.column_config.SelectboxColumn(options=COUNTRY_VALUES, required=True),
            "Region": st.column_config.TextColumn(),
            "Parent_Customer_ID": st.column_config.TextColumn(help="Relationship to another customer"),
            "Tax_ID": st.column_config.TextColumn(),
            "Effective_From": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Effective_To": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Domain": st.column_config.TextColumn(disabled=True),
            "Status": st.column_config.TextColumn(disabled=True),
            "Published_Version": st.column_config.TextColumn(disabled=True),
            "Last_Changed_By": st.column_config.TextColumn(disabled=True),
            "Last_Changed_At": st.column_config.TextColumn(disabled=True),
        }
    else:
        column_config = {
            "Product_ID": st.column_config.TextColumn(disabled=True, help="System-defined business key"),
            "Product_Name": st.column_config.TextColumn(required=True),
            "Category": st.column_config.TextColumn(required=True),
            "Is_Active": st.column_config.CheckboxColumn(),
            "GL_Code": st.column_config.TextColumn(),
            "Effective_From": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Effective_To": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Domain": st.column_config.TextColumn(disabled=True),
            "Status": st.column_config.TextColumn(disabled=True),
            "Published_Version": st.column_config.TextColumn(disabled=True),
            "Last_Changed_By": st.column_config.TextColumn(disabled=True),
            "Last_Changed_At": st.column_config.TextColumn(disabled=True),
        }

    edited = st.data_editor(
        editable_df,
        use_container_width=True,
        num_rows="dynamic",
        disabled=[c for c in editable_df.columns if c not in schema_cols],
        column_config=column_config,
        key=f"editor_{DOMAIN}"
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("Validate", use_container_width=True):
            issues = validate(edited, DOMAIN)
            if issues.empty:
                st.success("No validation issues found. Ready for submission.")
            else:
                st.warning(f"Found {len(issues)} issue(s).")
                st.dataframe(issues, use_container_width=True)
    with c2:
        if st.button("Submit Change Request", use_container_width=True):
            new_cr = {
                "CR_ID": f"CR-{500 + len(st.session_state.change_requests) + 1}",
                "Domain": DOMAIN,
                "Entity_Key": edited.iloc[-1]["Customer_ID"] if DOMAIN == "Customer" else edited.iloc[-1]["Product_ID"],
                "Change_Type": "Update",
                "Requested_By": ROLE.replace(" ", ".").lower(),
                "Approver": "data.owner",
                "Status": "Pending Approval",
                "Submitted_At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Environment": ENV
            }
            st.session_state.change_requests = pd.concat([st.session_state.change_requests, pd.DataFrame([new_cr])], ignore_index=True)
            st.success("Change request submitted for approval workflow.")
    with c3:
        st.caption("Typical flow: business edit -> steward validation -> approver signoff -> publish to curated Snowflake layer.")

# -----------------------------
# Change requests
# -----------------------------
elif page == "Change Requests":
    st.subheader("Access Control & Governance Workflow")
    st.write("Role-based approval queue for data stewards, owners, and administrators.")
    st.dataframe(st.session_state.change_requests, use_container_width=True)

    pending = st.session_state.change_requests[st.session_state.change_requests["Status"] == "Pending Approval"]
    if not pending.empty:
        selected = st.selectbox("Select pending CR", pending["CR_ID"].tolist())
        d1, d2, d3 = st.columns(3)
        with d1:
            if st.button("Approve", use_container_width=True):
                st.session_state.change_requests.loc[st.session_state.change_requests["CR_ID"] == selected, "Status"] = "Approved"
                st.success(f"{selected} approved.")
        with d2:
            if st.button("Reject", use_container_width=True):
                st.session_state.change_requests.loc[st.session_state.change_requests["CR_ID"] == selected, "Status"] = "Rejected"
                st.warning(f"{selected} rejected.")
        with d3:
            st.text_input("Comment", placeholder="Reason / approval note")
    else:
        st.success("No items waiting for approval.")

# -----------------------------
# Data quality
# -----------------------------
elif page == "Data Quality":
    st.subheader(f"{DOMAIN} Data Quality Rules")
    left, right = st.columns([1, 2])
    with left:
        st.markdown("**Configured rules**")
        for rule in RULES[DOMAIN]:
            st.write(f"- {rule}")
    with right:
        issues = validate(domain_frame(DOMAIN), DOMAIN)
        if issues.empty:
            st.success("Current published slice has no issues.")
        else:
            st.dataframe(issues, use_container_width=True)

# -----------------------------
# Metadata
# -----------------------------
elif page == "Metadata":
    st.subheader(f"{DOMAIN} Metadata Management")
    schema = SCHEMAS[DOMAIN]
    meta_df = pd.DataFrame([
        {"Column": col, "Data Type": schema["types"].get(col, "TEXT"), "Required": col in schema["required"], "Editable by Business": True if col in schema["columns"] else False}
        for col in schema["columns"]
    ])
    st.dataframe(meta_df, use_container_width=True)

    st.markdown("**Relationships**")
    if schema["relationships"]:
        for rel in schema["relationships"]:
            st.write(f"- {rel}")
    else:
        st.caption("No relationships configured for this domain in the current mock.")

    st.warning("Schema governance is centralized. New columns are introduced through admin-controlled metadata promotion, not end-user editing.")

# -----------------------------
# Governance
# -----------------------------
elif page == "Access & Governance":
    st.subheader("Role Model and Workflow Controls")
    access_df = pd.DataFrame([
        {"Role": "Business User", "Create/Edit Values": True, "Approve": False, "Publish": False, "Add/Remove Columns": False},
        {"Role": "Data Steward", "Create/Edit Values": True, "Approve": False, "Publish": False, "Add/Remove Columns": False},
        {"Role": "Approver", "Create/Edit Values": False, "Approve": True, "Publish": False, "Add/Remove Columns": False},
        {"Role": "MDM Admin", "Create/Edit Values": True, "Approve": True, "Publish": True, "Add/Remove Columns": True},
    ])
    st.dataframe(access_df, use_container_width=True)
    st.markdown("**Workflow**")
    st.write("1. Business-friendly edit in Dev workbench")
    st.write("2. Automated rule validation")
    st.write("3. Submit change request")
    st.write("4. Approval and audit trail")
    st.write("5. Publish curated version to Prod")

# -----------------------------
# Publish
# -----------------------------
elif page == "Publish / Versioning":
    st.subheader("Publication / Version Control")
    st.write("Separate Dev and Prod layers with explicit publish action for curated master data.")
    st.dataframe(st.session_state.release_log, use_container_width=True)

    p1, p2, p3 = st.columns(3)
    with p1:
        release_name = st.text_input("Release tag", value=f"v{len(st.session_state.release_log)+1}.0")
    with p2:
        promote_domain = st.selectbox("Domain to publish", ["Customer", "Product"])
    with p3:
        if st.button("Publish to Prod", use_container_width=True):
            release = {
                "Release": release_name,
                "Environment": "Prod",
                "Domain": promote_domain,
                "Published_By": ROLE.replace(" ", ".").lower(),
                "Published_At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Notes": "Published from approved Dev baseline"
            }
            st.session_state.release_log = pd.concat([pd.DataFrame([release]), st.session_state.release_log], ignore_index=True)
            st.success(f"Published {promote_domain} as {release_name} to Prod curated layer.")

# -----------------------------
# Snowflake landing
# -----------------------------
elif page == "Snowflake Landing":
    st.subheader("Snowflake Integration")
    st.code(
        """
RAW / STAGE -> MDM_DEV -> APPROVAL_QUEUE -> MDM_PROD_CURATED -> CONSUMPTION

Example publish pattern:
- Business edits stored in DEV working table
- Valid records flow through approval task / stream
- Approved snapshot written to curated PROD table
- Consumers read stable published version or current view
        """,
        language="sql"
    )

    landing_df = pd.DataFrame([
        {"Object": "MDM_DEV.CUSTOMER_WORKING", "Purpose": "Business-editable draft records", "Versioned": "Draft"},
        {"Object": "MDM_DEV.CHANGE_REQUESTS", "Purpose": "Approval workflow state", "Versioned": "N/A"},
        {"Object": "MDM_PROD.CUSTOMER_CURATED", "Purpose": "Published customer golden records", "Versioned": "Yes"},
        {"Object": "MDM_PROD.CUSTOMER_CURRENT_VW", "Purpose": "Latest approved view for consumers", "Versioned": "Current"},
    ])
    st.dataframe(landing_df, use_container_width=True)

    st.markdown("**Illustrative Snowflake-native pattern**")
    st.code(
        """
CREATE OR REPLACE TABLE MDM_DEV.CUSTOMER_WORKING (...);
CREATE OR REPLACE TABLE MDM_DEV.CHANGE_REQUESTS (...);
CREATE OR REPLACE TABLE MDM_PROD.CUSTOMER_CURATED (..., PUBLISHED_VERSION STRING);

-- publish action
INSERT INTO MDM_PROD.CUSTOMER_CURATED
SELECT *, 'v2.1' AS PUBLISHED_VERSION
FROM MDM_DEV.CUSTOMER_WORKING
WHERE VALIDATION_STATUS = 'PASS'
  AND APPROVAL_STATUS = 'APPROVED';
        """,
        language="sql"
    )

st.divider()
with st.expander("Design notes captured in this mock"):
    st.write("- Excel-like editing experience via grid editor")
    st.write("- Data quality rules and validation")
    st.write("- Locked column structure for governed schema")
    st.write("- Metadata-driven data types and relationships")
    st.write("- Access control and approvals")
    st.write("- Snowflake landing and curated publication")
    st.write("- Dev / Prod separation and explicit versioning")
