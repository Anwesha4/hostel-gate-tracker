
from pathlib import Path
from datetime import datetime, time

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hostel Gate Tracker",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Hostel Gate Tracker")
st.caption(
    "Review gate records, identify late returns, "
    "and find missing or inconsistent data."
)

REQUIRED_COLUMNS = [
    "Date", "Name", "RoomNo", "RollNo", "Hostel",
    "Purpose", "MobileNo", "OutTime", "InTime"
]

# --------------------------------------------------
# 1. Upload CSV or use the project CSV
# --------------------------------------------------
st.sidebar.header("Data source")

uploaded_file = st.sidebar.file_uploader(
    "Upload gate records (CSV)",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, dtype=str).fillna("")
        source_name = uploaded_file.name
    except Exception as exc:
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()
else:
    default_file = Path(__file__).parent / "data" / "data.csv"

    if not default_file.exists():
        st.info("Upload your data.csv using the sidebar.")
        st.stop()

    try:
        df = pd.read_csv(default_file, dtype=str).fillna("")
        source_name = "data/data.csv (project file)"
    except Exception as exc:
        st.error(f"Could not read the project CSV: {exc}")
        st.stop()

df.columns = df.columns.str.strip()

missing_columns = [
    col for col in REQUIRED_COLUMNS if col not in df.columns
]

if missing_columns:
    st.error(
        "The CSV is missing these columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

st.sidebar.success(f"Loaded: {source_name}")
st.sidebar.caption(f"{len(df)} records found")

if df.empty:
    st.warning("The selected CSV has no records.")
    st.stop()

# --------------------------------------------------
# 2. Parse dates and times
# --------------------------------------------------
def parse_date(value):
    if not value:
        return None

    result = pd.to_datetime(
        value, dayfirst=True, errors="coerce"
    )

    if pd.isna(result):
        return None

    return result.date()


def parse_time(value):
    if not value:
        return None

    formats = [
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p",
        "%I:%M:%S %p",
        "%I %p",
        "%H"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    return None


df["_date"] = df["Date"].apply(parse_date)
df["_out_time"] = df["OutTime"].apply(parse_time)
df["_in_time"] = df["InTime"].apply(parse_time)

# --------------------------------------------------
# 3. Configurable return deadline
# --------------------------------------------------
st.sidebar.header("Return deadline")

deadline = st.sidebar.time_input(
    "Set the deadline",
    value=time(21, 30),
    step=300
)

st.sidebar.caption(
    "Late returns are based on recorded return times "
    "that are later than this deadline."
)

# --------------------------------------------------
# 4. Identify data issues
# --------------------------------------------------
def find_issues(row):
    reasons = []

    # Missing essential information
    if not row["Date"]:
        reasons.append("Missing date")
    elif row["_date"] is None:
        reasons.append("Invalid date format")

    if not row["Name"]:
        reasons.append("Missing name")

    if not row["RoomNo"]:
        reasons.append("Missing room number")

    if not row["OutTime"]:
        reasons.append("Missing exit time")
    elif row["_out_time"] is None:
        reasons.append("Invalid exit time format")

    if not row["InTime"]:
        reasons.append("Return time not recorded")
    elif row["_in_time"] is None:
        reasons.append("Invalid return time format")

    # Potentially inconsistent time sequence
    out_time = row["_out_time"]
    in_time = row["_in_time"]

    if (
        out_time is not None
        and in_time is not None
        and out_time > in_time
    ):
        reasons.append(
            "Potentially inconsistent times: return time "
            "is earlier than exit time; check for an overnight return"
        )

    return "; ".join(reasons)


df["_issue_reasons"] = df.apply(find_issues, axis=1)

# --------------------------------------------------
# 5. Choose date
# --------------------------------------------------
valid_dates = sorted(df["_date"].dropna().unique())

if not valid_dates:
    st.error("No valid dates found in the Date column.")
    st.info("Check your date format, for example DD-MM-YYYY.")
    st.stop()

selected_date = st.selectbox(
    "Select date to review",
    options=valid_dates,
    index=len(valid_dates) - 1,
    format_func=lambda d: d.strftime("%d %b %Y")
)

daily = df[df["_date"] == selected_date].copy()

# --------------------------------------------------
# 6. Analyze selected day's records
# --------------------------------------------------
no_return_recorded = daily[
    daily["OutTime"].ne("") & daily["InTime"].eq("")
]

late_returns = daily[
    daily["_in_time"].apply(
        lambda t: t is not None and t > deadline
    )
]

data_issues = daily[daily["_issue_reasons"].ne("")].copy()

# --------------------------------------------------
# 7. Daily overview
# --------------------------------------------------
st.subheader("Daily overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total records", len(daily))
c2.metric("Data issues to review", len(data_issues))
c3.metric("Late recorded returns", len(late_returns))
c4.metric("No return time recorded", len(no_return_recorded))

st.caption(
    f"Selected deadline: {deadline.strftime('%I:%M %p').lstrip('0')}. "
    "Missing return times do not confirm that a student is still outside."
)

# --------------------------------------------------
# 8. Busiest entry and exit periods
# --------------------------------------------------
st.subheader("🕒 Busiest gate movement periods")
st.write("Each bar represents one hour of recorded gate movements.")


def hourly_counts(series):
    hours = series.dropna().apply(lambda t: t.hour)

    if hours.empty:
        return pd.DataFrame(columns=["Time period", "Records"])

    counts = hours.value_counts().sort_index()

    return pd.DataFrame({
        "Time period": [
            f"{hour:02d}:00–{hour:02d}:59"
            for hour in counts.index
        ],
        "Records": counts.values
    })


out_chart, in_chart = st.columns(2)

with out_chart:
    st.markdown("**🚪 Recorded exits — OutTime**")
    out_counts = hourly_counts(daily["_out_time"])

    if out_counts.empty:
        st.info("No valid exit times for this date.")
    else:
        st.bar_chart(
            out_counts.set_index("Time period"),
            y="Records",
            x_label="Hour",
            y_label="Number of exits"
        )

        busiest = out_counts.loc[out_counts["Records"].idxmax()]
        st.write(
            f"**Busiest exit period:** {busiest['Time period']} "
            f"({busiest['Records']} records)"
        )

with in_chart:
    st.markdown("**🏠 Recorded entries — InTime**")
    in_counts = hourly_counts(daily["_in_time"])

    if in_counts.empty:
        st.info("No valid entry times for this date.")
    else:
        st.bar_chart(
            in_counts.set_index("Time period"),
            y="Records",
            x_label="Hour",
            y_label="Number of entries"
        )

        busiest = in_counts.loc[in_counts["Records"].idxmax()]
        st.write(
            f"**Busiest entry period:** {busiest['Time period']} "
            f"({busiest['Records']} records)"
        )

st.caption(
    "Charts use valid recorded times only. They may not represent "
    "all actual gate movements."
)

# --------------------------------------------------
# 9. Records needing attention
# --------------------------------------------------
st.subheader("Records needing attention")


def safe_display(frame):
    return frame.drop(
        columns=[
            "MobileNo", "_date", "_out_time",
            "_in_time", "_issue_reasons"
        ],
        errors="ignore"
    )


tab1, tab2 = st.tabs([
    "Data Issues to Review",
    "Late Returns"
])

with tab1:
    st.write(
        "This combined list includes missing information, invalid "
        "dates or times, and potentially inconsistent time sequences. "
        "Check the reason before deciding whether a record needs correction."
    )

    if data_issues.empty:
        st.success("No data issues detected for this date.")
    else:
        display_issues = safe_display(data_issues).copy()
        display_issues.insert(
            0,
            "Issue",
            data_issues["_issue_reasons"].values
        )

        st.dataframe(
            display_issues,
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.write(
        f"Records with a valid recorded return time after "
        f"{deadline.strftime('%I:%M %p').lstrip('0')}."
    )

    if late_returns.empty:
        st.info("No late recorded returns detected for this date.")
    else:
        st.dataframe(
            safe_display(late_returns),
            use_container_width=True,
            hide_index=True
        )

# --------------------------------------------------
# 10. Search records
# --------------------------------------------------
st.subheader("🔎 Find a student")

query = st.text_input(
    "Search by name, room number, or roll number"
).strip().lower()

if query:
    matches = daily[
        daily[["Name", "RoomNo", "RollNo"]]
        .apply(
            lambda col: col.str.lower().str.contains(
                query, regex=False, na=False
            )
        )
        .any(axis=1)
    ]

    st.dataframe(
        safe_display(matches),
        use_container_width=True,
        hide_index=True
    )

    if matches.empty:
        st.info("No matching records found.")
else:
    st.caption("Enter a search term to find a matching record.")

st.divider()
st.caption(
    "Hostel Gate Tracker is a record-review aid. It does not verify "
    "actual student whereabouts or replace the official hostel register."
)
