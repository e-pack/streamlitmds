import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MDS Console",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #155195;
    border-right: 1px solid #0f3e75;
}
section[data-testid="stSidebar"] * { color: #ffffff !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 13px !important; padding: 4px 0; }
section[data-testid="stSidebar"] .stSelectbox label { font-size: 11px !important; opacity: .75; }
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] * {
    background-color: #0f3e75 !important;
    color: #ffffff !important;
    border-color: #1a65b8 !important;
}

/* ── App background ── */
.stApp { background-color: #f5f7fa; color: #1a1f2e; }

/* Main content area white card effect */
section.main > div { background-color: #ffffff; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #dde3ed;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 1px 3px rgba(21,81,149,.06);
}
[data-testid="metric-container"] label {
    color: #6b7a99 !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: .06em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #155195 !important; font-size: 24px !important; font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11px !important; color: #6b7a99 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #dde3ed; border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(21,81,149,.04);
}

/* ── Buttons ── */
.stButton > button {
    background-color: #ffffff; color: #374161;
    border: 1px solid #c8d0e0; border-radius: 6px;
    font-family: 'IBM Plex Sans', sans-serif; font-size: 13px;
    padding: 5px 16px; transition: all .15s;
}
.stButton > button:hover {
    background-color: #eef2fa; border-color: #155195; color: #155195;
}

.primary-btn > button {
    background-color: #155195 !important; border-color: #155195 !important; color: #ffffff !important;
}
.primary-btn > button:hover { background-color: #0f3e75 !important; }

.approve-btn > button {
    background-color: #1a7f37 !important; border-color: #1a7f37 !important;
    color: #ffffff !important; font-size: 12px !important;
}
.approve-btn > button:hover { background-color: #166429 !important; }

.reject-btn > button {
    background-color: #cf222e !important; border-color: #cf222e !important;
    color: #ffffff !important; font-size: 12px !important;
}
.reject-btn > button:hover { background-color: #a40e26 !important; }

/* ── Form inputs ── */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background-color: #ffffff !important; color: #1a1f2e !important;
    border: 1px solid #c8d0e0 !important; border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important; font-size: 13px !important;
}
.stTextInput input:focus, .stSelectbox select:focus {
    border-color: #155195 !important;
    box-shadow: 0 0 0 3px rgba(21,81,149,.12) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent; border-bottom: 1px solid #dde3ed; gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent; color: #6b7a99;
    font-size: 13px; padding: 8px 16px; border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #155195 !important; border-bottom: 2px solid #155195 !important;
    background: transparent !important; font-weight: 500 !important;
}

/* ── Typography ── */
.page-title    { font-size: 22px; font-weight: 600; color: #1a1f2e; margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: #6b7a99; margin-bottom: 20px; }
.section-header {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 500;
    color: #6b7a99; text-transform: uppercase; letter-spacing: .1em;
    margin: 20px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #dde3ed;
}

/* ── Info / warning boxes ── */
.info-box {
    background: #eef4ff; border: 1px solid #b3ccee; border-radius: 8px;
    padding: 12px 16px; font-size: 13px; color: #155195; margin: 12px 0;
}
.warn-box {
    background: #fff8e6; border: 1px solid #f0c060; border-radius: 8px;
    padding: 12px 16px; font-size: 13px; color: #7a5100; margin: 12px 0;
}

/* ── Audit entries ── */
.audit-entry {
    background: #ffffff; border: 1px solid #dde3ed; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 8px; font-size: 13px;
    box-shadow: 0 1px 2px rgba(21,81,149,.04);
}

/* ── Divider ── */
hr { border-color: #dde3ed !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #f5f7fa; border: 1px dashed #b3ccee; border-radius: 8px;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid #dde3ed !important; border-radius: 8px !important;
    background: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def short_id(prefix):
    return f"{prefix}-{str(uuid.uuid4())[:5].upper()}"


# ── Seed data ─────────────────────────────────────────────────────────────────
def seed_customers():
    return pd.DataFrame([
        {"ID":"CUST-A1B2C","Name":"Apex Manufacturing LLC",  "Segment":"Enterprise", "Region":"Midwest",   "Contact":"Sarah Okafor",  "Email":"s.okafor@apexmfg.com",     "Status":"Active",   "Modified":"2026-03-28","Modified By":"m.patel"},
        {"ID":"CUST-D3E4F","Name":"Riverstone Retail Group", "Segment":"Mid-Market", "Region":"Southeast", "Contact":"James Liu",      "Email":"j.liu@riverstone.com",      "Status":"Active",   "Modified":"2026-03-27","Modified By":"t.okafor"},
        {"ID":"CUST-G5H6I","Name":"Nordic Logistics Co.",    "Segment":"Enterprise", "Region":"Northeast", "Contact":"Elsa Varga",     "Email":"e.varga@nordic-log.com",    "Status":"Inactive", "Modified":"2026-03-22","Modified By":"m.patel"},
        {"ID":"CUST-J7K8L","Name":"Summit Distributors",     "Segment":"SMB",        "Region":"West",      "Contact":"Carlos Mendez",  "Email":"c.mendez@summitdist.com",   "Status":"Active",   "Modified":"2026-03-20","Modified By":"a.chen"},
        {"ID":"CUST-M9N0O","Name":"Hartley Foods Inc.",      "Segment":"Mid-Market", "Region":"South",     "Contact":"Priya Sharma",   "Email":"p.sharma@hartleyfoods.com", "Status":"Active",   "Modified":"2026-03-18","Modified By":"j.kim"},
        {"ID":"CUST-P1Q2R","Name":"BlueCrest Partners",      "Segment":"Enterprise", "Region":"Northeast", "Contact":"Tom Fischer",    "Email":"t.fischer@bluecrest.com",   "Status":"Inactive", "Modified":"2026-03-15","Modified By":"t.okafor"},
    ])

def seed_products():
    return pd.DataFrame([
        {"ID":"SKU-10042","Name":'Industrial Valve 3/4"', "Category":"Hardware",    "UOM":"EA",  "List Price":"$42.00",  "Status":"Active",       "Modified":"2026-03-29","Modified By":"a.chen"},
        {"ID":"SKU-09981","Name":"Hydraulic Seal Kit",    "Category":"Maintenance", "UOM":"KIT", "List Price":"$118.50", "Status":"Active",       "Modified":"2026-03-27","Modified By":"m.patel"},
        {"ID":"SKU-09874","Name":'Conveyor Belt 24"',     "Category":"Equipment",   "UOM":"FT",  "List Price":"$9.75",   "Status":"Discontinued", "Modified":"2026-03-22","Modified By":"j.kim"},
        {"ID":"SKU-10101","Name":"Pressure Gauge 100PSI", "Category":"Instruments", "UOM":"EA",  "List Price":"$67.00",  "Status":"Active",       "Modified":"2026-03-19","Modified By":"a.chen"},
        {"ID":"SKU-10088","Name":"Grease Fitting Pack",   "Category":"Maintenance", "UOM":"BOX", "List Price":"$14.25",  "Status":"Active",       "Modified":"2026-03-17","Modified By":"t.okafor"},
    ])

def seed_vendors():
    return pd.DataFrame([
        {"ID":"VEND-00204","Name":"Global Parts Supply Co.","Category":"Raw Materials","Contact":"R. Santos", "Email":"r.santos@gps.com",   "Status":"Active",   "Modified":"2026-03-29","Modified By":"m.patel"},
        {"ID":"VEND-00198","Name":"Midwest Tool & Die",     "Category":"Services",     "Contact":"D. Krueger","Email":"d.krueger@mwtd.com", "Status":"Active",   "Modified":"2026-03-22","Modified By":"a.chen"},
        {"ID":"VEND-00189","Name":"Atlas Freight Partners", "Category":"Logistics",    "Contact":"M. Diallo", "Email":"m.diallo@atlas.com", "Status":"Inactive", "Modified":"2026-03-10","Modified By":"j.kim"},
        {"ID":"VEND-00177","Name":"PacRim Electronics",     "Category":"Equipment",    "Contact":"S. Tanaka", "Email":"s.tanaka@pacrim.com","Status":"Active",   "Modified":"2026-03-05","Modified By":"t.okafor"},
    ])

def seed_locations():
    return pd.DataFrame([
        {"ID":"LOC-00041","Name":"Columbus Distribution Hub","Type":"Warehouse","Address":"1200 Polaris Pkwy",   "City":"Columbus",  "State":"OH","Status":"Active",   "Modified":"2026-03-29","Modified By":"m.patel"},
        {"ID":"LOC-00038","Name":"Cleveland Retail Center",  "Type":"Store",    "Address":"4401 Rockside Rd",    "City":"Cleveland", "State":"OH","Status":"Active",   "Modified":"2026-03-25","Modified By":"a.chen"},
        {"ID":"LOC-00031","Name":"Cincinnati Office",        "Type":"Office",   "Address":"525 Vine St Ste 1800","City":"Cincinnati","State":"OH","Status":"Active",   "Modified":"2026-03-20","Modified By":"j.kim"},
        {"ID":"LOC-00027","Name":"Dayton Warehouse",         "Type":"Warehouse","Address":"801 E 2nd St",         "City":"Dayton",    "State":"OH","Status":"Inactive", "Modified":"2026-03-01","Modified By":"t.okafor"},
    ])

def seed_staging():
    return pd.DataFrame([
        {"ID":"STG-001","Domain":"Customers","Record ID":"CUST-NEW01","Record Name":"Nordic Logistics Co.",       "Change Type":"New Record","Status":"Pending","Submitted By":"j.kim",   "Submitted At":"2026-03-26 09:14","Reviewed By":"","Reviewed At":"","Payload":json.dumps({"Name":"Nordic Logistics Co.","Segment":"Enterprise","Region":"Northeast","Contact":"Elsa Varga","Email":"e.varga@nordic.com","Status":"Active"}),"Notes":""},
        {"ID":"STG-002","Domain":"Customers","Record ID":"CUST-A1B2C","Record Name":"Apex Manufacturing LLC",    "Change Type":"Edit",       "Status":"Pending","Submitted By":"t.okafor","Submitted At":"2026-03-25 14:02","Reviewed By":"","Reviewed At":"","Payload":json.dumps({"Region":"Midwest (was: Southeast)"}),"Notes":"Region correction per account team"},
        {"ID":"STG-003","Domain":"Products", "Record ID":"SKU-NEW01", "Record Name":'Pressure Relief Valve 1/2"',"Change Type":"New Record","Status":"Pending","Submitted By":"a.chen",  "Submitted At":"2026-03-24 11:30","Reviewed By":"","Reviewed At":"","Payload":json.dumps({"Name":'Pressure Relief Valve 1/2"',"Category":"Hardware","UOM":"EA","List Price":"$54.00","Status":"Active"}),"Notes":""},
    ])

def seed_audit():
    return [
        {"ts":"2026-03-28 10:42","actor":"m.patel",  "action":"Approved edit on CUST-A1B2C — Region: Southeast → Midwest",       "domain":"Customers","type":"Approved"},
        {"ts":"2026-03-27 15:10","actor":"m.patel",  "action":"Approved new record CUST-D3E4F (Riverstone Retail Group)",         "domain":"Customers","type":"Approved"},
        {"ts":"2026-03-25 14:02","actor":"t.okafor", "action":"Submitted edit on CUST-A1B2C — Region correction",                 "domain":"Customers","type":"Submitted"},
        {"ts":"2026-03-24 11:30","actor":"a.chen",   "action":'Submitted new product SKU-NEW01 (Pressure Relief Valve 1/2")',     "domain":"Products", "type":"Submitted"},
        {"ts":"2026-03-22 09:00","actor":"j.kim",    "action":"Rejected new record — duplicate email detected (VEND-00204)",      "domain":"Vendors",  "type":"Rejected"},
        {"ts":"2026-03-20 16:45","actor":"m.patel",  "action":"Approved status change CUST-P1Q2R → Inactive",                    "domain":"Customers","type":"Approved"},
        {"ts":"2026-03-18 08:30","actor":"a.chen",   "action":"Submitted new location LOC-00041 (Columbus Distribution Hub)",     "domain":"Locations","type":"Submitted"},
        {"ts":"2026-03-15 11:20","actor":"r.santos", "action":"Approved new vendor VEND-00204 (Global Parts Supply Co.)",         "domain":"Vendors",  "type":"Approved"},
    ]


# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "customers": seed_customers(),
        "products":  seed_products(),
        "vendors":   seed_vendors(),
        "locations": seed_locations(),
        "staging":   seed_staging(),
        "audit":     seed_audit(),
        "user_role": "MDS_STEWARD",
        "user_name": "m.patel",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Domain config ─────────────────────────────────────────────────────────────
DOMAIN_CONFIG = {
    "Customers": {
        "df_key": "customers",
        "prefix": "CUST",
        "display_cols": ["ID","Name","Segment","Region","Contact","Email","Status","Modified","Modified By"],
        "fields": [
            ("Name",    "text",   "Company name",                                            True),
            ("Segment", "select", ["Enterprise","Mid-Market","SMB"],                         False),
            ("Region",  "select", ["Northeast","Southeast","Midwest","South","West"],        False),
            ("Contact", "text",   "Primary contact name",                                   False),
            ("Email",   "text",   "contact@company.com",                                    False),
            ("Status",  "select", ["Active","Inactive"],                                     False),
        ],
    },
    "Products": {
        "df_key": "products",
        "prefix": "SKU",
        "display_cols": ["ID","Name","Category","UOM","List Price","Status","Modified","Modified By"],
        "fields": [
            ("Name",       "text",   "Product name",                                              True),
            ("Category",   "select", ["Hardware","Maintenance","Equipment","Instruments","Materials"], False),
            ("UOM",        "select", ["EA","KIT","BOX","FT","LB"],                               False),
            ("List Price", "text",   "$0.00",                                                    False),
            ("Status",     "select", ["Active","Discontinued"],                                  False),
        ],
    },
    "Vendors": {
        "df_key": "vendors",
        "prefix": "VEND",
        "display_cols": ["ID","Name","Category","Contact","Email","Status","Modified","Modified By"],
        "fields": [
            ("Name",     "text",   "Vendor name",                                         True),
            ("Category", "select", ["Raw Materials","Services","Equipment","Logistics"],   False),
            ("Contact",  "text",   "Contact name",                                        False),
            ("Email",    "text",   "contact@vendor.com",                                  False),
            ("Status",   "select", ["Active","Inactive"],                                 False),
        ],
    },
    "Locations": {
        "df_key": "locations",
        "prefix": "LOC",
        "display_cols": ["ID","Name","Type","Address","City","State","Status","Modified","Modified By"],
        "fields": [
            ("Name",    "text",   "Location name",                                        True),
            ("Type",    "select", ["Warehouse","Store","Office","Distribution"],           False),
            ("Address", "text",   "Street address",                                       True),
            ("City",    "text",   "City",                                                 False),
            ("State",   "select", ["OH","IN","KY","MI","IL","PA","NY","TX","CA","WA"],    False),
            ("Status",  "select", ["Active","Inactive"],                                  False),
        ],
    },
}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔷 MDS Console")
    st.markdown("---")
    st.markdown('<div class="section-header">Session</div>', unsafe_allow_html=True)

    role = st.selectbox("Active role", ["MDS_STEWARD","MDS_CONTRIBUTOR"])
    st.session_state.user_role = role

    uname = st.selectbox("Logged in as", ["m.patel","j.kim","t.okafor","a.chen","r.santos"])
    st.session_state.user_name = uname

    st.markdown("---")
    st.markdown('<div class="section-header">Domains</div>', unsafe_allow_html=True)

    pending_count = len(st.session_state.staging[st.session_state.staging["Status"] == "Pending"])

    page = st.radio(
        "nav",
        ["Customers","Products","Vendors","Locations","—","Pending Review","Audit Log","Bulk Import"],
        label_visibility="collapsed",
    )

    if pending_count > 0:
        st.markdown(f'<div class="warn-box">⏳ {pending_count} record(s) awaiting review</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Mock mode — no Snowflake connection")


# ════════════════════════════════════════════════════════════════════════════════
# Domain page
# ════════════════════════════════════════════════════════════════════════════════
def render_domain_page(domain):
    cfg   = DOMAIN_CONFIG[domain]
    df    = st.session_state[cfg["df_key"]]
    uname = st.session_state.user_name

    # Header row
    col_title, col_btn = st.columns([6, 1])
    with col_title:
        st.markdown(f'<div class="page-title">{domain}</div>', unsafe_allow_html=True)
        total   = len(df)
        active  = len(df[df["Status"] == "Active"])
        pending = len(st.session_state.staging[
            (st.session_state.staging["Domain"] == domain) &
            (st.session_state.staging["Status"] == "Pending")
        ])
        st.markdown(f'<div class="page-subtitle">{total} records · {active} active · {pending} pending review</div>', unsafe_allow_html=True)
    with col_btn:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        add_clicked = st.button("＋ Add record", key=f"add_{domain}", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Stat cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records",  f"{total:,}")
    m2.metric("Active",         f"{active:,}", f"{round(active/total*100)}% of total" if total else "")
    m3.metric("Inactive",       f"{total-active:,}")
    m4.metric("Pending Review", f"{pending}")

    st.markdown("---")

    # Tabs
    tab_all, tab_active, tab_inactive = st.tabs(["All records", "Active", "Inactive"])

    def show_table(tab, status_filter=None):
        with tab:
            data = df if status_filter is None else df[df["Status"] == status_filter]
            search = st.text_input("", placeholder=f"🔍  Search {domain.lower()}...",
                                   key=f"search_{domain}_{status_filter}", label_visibility="collapsed")
            if search:
                mask = data.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
                data = data[mask]
            st.dataframe(data[cfg["display_cols"]], use_container_width=True, hide_index=True,
                         column_config={"Modified": st.column_config.DateColumn("Modified", format="MMM DD, YYYY")})
            st.caption(f"{len(data)} records")

    show_table(tab_all)
    show_table(tab_active, "Active")
    show_table(tab_inactive, "Inactive")

    # Add record form
    if add_clicked:
        st.session_state[f"show_form_{domain}"] = True

    if st.session_state.get(f"show_form_{domain}"):
        st.markdown("---")
        st.markdown(f'<div class="section-header">New record — {domain}</div>', unsafe_allow_html=True)

        with st.form(key=f"form_{domain}", clear_on_submit=True):
            values = {}
            fields = cfg["fields"]
            i = 0
            while i < len(fields):
                fname, ftype, fopts, full = fields[i]
                if full:
                    values[fname] = st.text_input(fname, placeholder=fopts if isinstance(fopts, str) else "") \
                        if ftype == "text" else st.selectbox(fname, fopts)
                    i += 1
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        values[fname] = st.text_input(fname, placeholder=fopts if isinstance(fopts, str) else "") \
                            if ftype == "text" else st.selectbox(fname, fopts)
                    i += 1
                    if i < len(fields) and not fields[i][3]:
                        fname2, ftype2, fopts2, _ = fields[i]
                        with c2:
                            values[fname2] = st.text_input(fname2, placeholder=fopts2 if isinstance(fopts2, str) else "") \
                                if ftype2 == "text" else st.selectbox(fname2, fopts2)
                        i += 1

            notes = st.text_area("Notes (optional)", placeholder="Context for the reviewing steward...")

            col_cancel, _, col_draft, col_submit = st.columns([1, 3, 1.5, 1.5])
            cancel = col_cancel.form_submit_button("Cancel")
            draft  = col_draft.form_submit_button("Save draft")
            submit = col_submit.form_submit_button("Submit for review", type="primary")

            if cancel:
                st.session_state[f"show_form_{domain}"] = False
                st.rerun()

            if submit or draft:
                name_val = values.get("Name", "").strip()
                if not name_val:
                    st.error("Name is required.")
                else:
                    new_id  = short_id(cfg["prefix"])
                    stg_id  = f"STG-{str(uuid.uuid4())[:4].upper()}"
                    status  = "Pending" if submit else "Draft"
                    new_stg = {
                        "ID": stg_id, "Domain": domain,
                        "Record ID": new_id, "Record Name": name_val,
                        "Change Type": "New Record", "Status": status,
                        "Submitted By": uname, "Submitted At": now_str(),
                        "Reviewed By": "", "Reviewed At": "",
                        "Payload": json.dumps(values), "Notes": notes,
                    }
                    st.session_state.staging = pd.concat(
                        [st.session_state.staging, pd.DataFrame([new_stg])], ignore_index=True)
                    st.session_state.audit.insert(0, {
                        "ts": now_str(), "actor": uname,
                        "action": f"Submitted new {domain[:-1]} record — {name_val} ({new_id})",
                        "domain": domain, "type": "Submitted",
                    })
                    st.session_state[f"show_form_{domain}"] = False
                    label = "staged for review" if submit else "saved as draft"
                    st.success(f"✓ Record {label}. Assigned ID: `{new_id}`")
                    st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# Pending Review
# ════════════════════════════════════════════════════════════════════════════════
def render_review():
    uname = st.session_state.user_name
    role  = st.session_state.user_role

    st.markdown('<div class="page-title">Pending Review</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Records submitted by contributors, awaiting steward approval before writing to master tables</div>', unsafe_allow_html=True)

    if role != "MDS_STEWARD":
        st.markdown('<div class="warn-box">⚠️ You need the MDS_STEWARD role to approve or reject records. Switch your role in the sidebar.</div>', unsafe_allow_html=True)

    pending = st.session_state.staging[st.session_state.staging["Status"] == "Pending"].copy()

    if pending.empty:
        st.success("✓ No records pending review.")
        return

    st.markdown(f"**{len(pending)} record(s) awaiting action**")
    st.markdown("---")

    for _, row in pending.iterrows():
        icon  = "🆕" if row["Change Type"] == "New Record" else "✏️"
        label = f"{icon}  **{row['Record Name']}**  ·  {row['Domain']}  ·  submitted by `{row['Submitted By']}`  ·  {row['Submitted At']}"

        with st.expander(label, expanded=True):
            c_detail, c_actions = st.columns([4, 1])

            with c_detail:
                st.markdown(f"**Change type:** {row['Change Type']}  &nbsp;·&nbsp;  **Assigned ID:** `{row['Record ID']}`")
                try:
                    payload = json.loads(row["Payload"])
                    st.markdown("**Proposed values:**")
                    for k, v in payload.items():
                        st.markdown(f"&emsp;`{k}` → **{v}**")
                except Exception:
                    st.code(row["Payload"])
                if row["Notes"]:
                    st.markdown(f"**Submitter notes:** {row['Notes']}")

            with c_actions:
                if role == "MDS_STEWARD":
                    st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
                    if st.button("✓ Approve", key=f"approve_{row['ID']}"):
                        idx = st.session_state.staging.index[st.session_state.staging["ID"] == row["ID"]].tolist()[0]
                        st.session_state.staging.at[idx, "Status"]      = "Approved"
                        st.session_state.staging.at[idx, "Reviewed By"] = uname
                        st.session_state.staging.at[idx, "Reviewed At"] = now_str()

                        # Write to master on new record approval
                        if row["Change Type"] == "New Record":
                            cfg = DOMAIN_CONFIG[row["Domain"]]
                            try:
                                payload = json.loads(row["Payload"])
                            except Exception:
                                payload = {}
                            master_row = {"ID": row["Record ID"], **payload,
                                          "Modified": now_str()[:10], "Modified By": uname}
                            existing = st.session_state[cfg["df_key"]]
                            for col in existing.columns:
                                if col not in master_row:
                                    master_row[col] = ""
                            st.session_state[cfg["df_key"]] = pd.concat(
                                [existing, pd.DataFrame([master_row])], ignore_index=True)

                        st.session_state.audit.insert(0, {
                            "ts": now_str(), "actor": uname,
                            "action": f"Approved {row['Change Type'].lower()} — {row['Record Name']} ({row['Record ID']})",
                            "domain": row["Domain"], "type": "Approved",
                        })
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="reject-btn">', unsafe_allow_html=True)
                    if st.button("✕ Reject", key=f"reject_{row['ID']}"):
                        idx = st.session_state.staging.index[st.session_state.staging["ID"] == row["ID"]].tolist()[0]
                        st.session_state.staging.at[idx, "Status"]      = "Rejected"
                        st.session_state.staging.at[idx, "Reviewed By"] = uname
                        st.session_state.staging.at[idx, "Reviewed At"] = now_str()
                        st.session_state.audit.insert(0, {
                            "ts": now_str(), "actor": uname,
                            "action": f"Rejected {row['Change Type'].lower()} — {row['Record Name']} ({row['Record ID']})",
                            "domain": row["Domain"], "type": "Rejected",
                        })
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.caption("Steward role required to act")


# ════════════════════════════════════════════════════════════════════════════════
# Audit Log
# ════════════════════════════════════════════════════════════════════════════════
def render_audit():
    st.markdown('<div class="page-title">Audit Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Immutable record of all create, edit, approve, and reject actions across all domains</div>', unsafe_allow_html=True)

    log = st.session_state.audit

    fc1, fc2, _ = st.columns([2, 2, 4])
    domain_filter = fc1.selectbox("Domain", ["All","Customers","Products","Vendors","Locations"])
    type_filter   = fc2.selectbox("Action type", ["All","Submitted","Approved","Rejected"])

    filtered = [e for e in log
                if (domain_filter == "All" or e["domain"] == domain_filter)
                and (type_filter  == "All" or e["type"]   == type_filter)]

    st.markdown(f"**{len(filtered)} entries**")
    st.markdown("---")

    type_colors = {"Approved": "#1a7f37", "Rejected": "#cf222e", "Submitted": "#155195"}

    for entry in filtered:
        color = type_colors.get(entry["type"], "#6b7a99")
        st.markdown(f"""
        <div class="audit-entry">
            <span style="color:{color};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em">{entry['type']}</span>
            &nbsp;·&nbsp;<span style="color:#6b7a99;font-size:11px;font-family:'IBM Plex Mono',monospace">{entry['ts']}</span>
            &nbsp;·&nbsp;<span style="color:#155195;font-weight:500">{entry['actor']}</span>
            <div style="margin-top:5px;color:#1a1f2e">{entry['action']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if filtered:
        csv = pd.DataFrame(filtered).to_csv(index=False)
        st.download_button("⬇ Export audit log (CSV)", data=csv,
                           file_name="mds_audit_log.csv", mime="text/csv")


# ════════════════════════════════════════════════════════════════════════════════
# Bulk Import
# ════════════════════════════════════════════════════════════════════════════════
def render_import():
    uname = st.session_state.user_name

    st.markdown('<div class="page-title">Bulk Import</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Upload a CSV to stage multiple records for review. Invalid rows are returned as an error report before anything is committed.</div>', unsafe_allow_html=True)

    domain = st.selectbox("Target domain", ["Customers","Products","Vendors","Locations"])

    TEMPLATES = {
        "Customers": "Name,Segment,Region,Contact,Email,Status\nAcme Corp,Enterprise,Midwest,John Doe,j.doe@acme.com,Active\nBeta LLC,SMB,West,Jane Smith,j.smith@beta.com,Active",
        "Products":  "Name,Category,UOM,List Price,Status\nWidget A,Hardware,EA,$10.00,Active\nSeal Kit B,Maintenance,KIT,$45.00,Active",
        "Vendors":   "Name,Category,Contact,Email,Status\nParts Co,Raw Materials,Jane Doe,j.doe@parts.com,Active",
        "Locations": "Name,Type,Address,City,State,Status\nMain Office,Office,100 Main St,Columbus,OH,Active",
    }

    col_dl, _ = st.columns([2, 4])
    with col_dl:
        st.download_button(
            f"⬇ Download {domain} template",
            data=TEMPLATES[domain],
            file_name=f"mds_{domain.lower()}_template.csv",
            mime="text/csv",
        )

    st.markdown('<div class="info-box">ℹ️ Rows with missing Name or invalid Email will be flagged in an error report. Valid rows proceed to staging independently.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        try:
            df_upload = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not parse file: {e}")
            return

        st.markdown(f"**{len(df_upload)} rows detected — preview:**")
        st.dataframe(df_upload.head(10), use_container_width=True, hide_index=True)

        # Validate
        errors, valid_rows = [], []
        for i, row in df_upload.iterrows():
            errs = []
            name = str(row.get("Name", "")).strip()
            if not name:
                errs.append("Name is required")
            email = str(row.get("Email", ""))
            if email and "@" not in email:
                errs.append("Invalid email format")
            if errs:
                errors.append({"Row": i+2, "Name": name or "(blank)", "Issues": "; ".join(errs)})
            else:
                valid_rows.append(row)

        m1, m2 = st.columns(2)
        m1.metric("Valid rows",  len(valid_rows))
        m2.metric("Error rows", len(errors))

        if errors:
            st.warning(f"{len(errors)} row(s) have validation errors and will not be staged.")
            st.dataframe(pd.DataFrame(errors), use_container_width=True, hide_index=True)
            st.download_button("⬇ Download error report", data=pd.DataFrame(errors).to_csv(index=False),
                               file_name="mds_import_errors.csv", mime="text/csv")

        if valid_rows:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button(f"Stage {len(valid_rows)} valid row(s) for review"):
                cfg = DOMAIN_CONFIG[domain]
                for row in valid_rows:
                    new_id  = short_id(cfg["prefix"])
                    stg_id  = f"STG-{str(uuid.uuid4())[:4].upper()}"
                    payload = {k: str(v) for k, v in row.items() if pd.notna(v)}
                    new_stg = {
                        "ID": stg_id, "Domain": domain,
                        "Record ID": new_id, "Record Name": str(row.get("Name", "")),
                        "Change Type": "New Record", "Status": "Pending",
                        "Submitted By": uname, "Submitted At": now_str(),
                        "Reviewed By": "", "Reviewed At": "",
                        "Payload": json.dumps(payload), "Notes": "Bulk import batch",
                    }
                    st.session_state.staging = pd.concat(
                        [st.session_state.staging, pd.DataFrame([new_stg])], ignore_index=True)
                st.session_state.audit.insert(0, {
                    "ts": now_str(), "actor": uname,
                    "action": f"Bulk import — {len(valid_rows)} {domain.lower()} records staged for review",
                    "domain": domain, "type": "Submitted",
                })
                st.success(f"✓ {len(valid_rows)} records staged. Go to Pending Review to approve.")
            st.markdown('</div>', unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────
if page in DOMAIN_CONFIG:
    render_domain_page(page)
elif page == "Pending Review":
    render_review()
elif page == "Audit Log":
    render_audit()
elif page == "Bulk Import":
    render_import()
