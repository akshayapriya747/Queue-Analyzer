import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
from io import BytesIO

st.set_page_config(page_title="Hospital Waiting Time Analyzer", page_icon="🏥", layout="wide")

st.title("🏥 Hospital Patient Waiting Time Analyzer")
st.write("Enter patient details below. The app analyzes the data you enter and generates a downloadable report.")

if "patients" not in st.session_state:
    st.session_state.patients = []

with st.form("patient_form", clear_on_submit=True):
    st.subheader("Enter Patient Details")
    col1, col2 = st.columns(2)
    with col1:
        patient_id = st.text_input("Patient ID", placeholder="Example: P101")
        department = st.selectbox(
            "Department",
            ["Cardiology", "Neurology", "Orthopedics", "Pediatrics",
             "General Medicine", "Dermatology", "Other"]
        )
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    with col2:
        patient_name = st.text_input("Patient name (optional)")
        patient_date = st.date_input("Visit date", value=date.today())
        waiting_time = st.number_input(
            "Waiting time (minutes)", min_value=0, max_value=1440, value=10, step=1
        )
    submitted = st.form_submit_button("Add Patient")

    if submitted:
        if not patient_id.strip():
            st.error("Please enter a Patient ID.")
        elif any(p["Patient ID"] == patient_id.strip() for p in st.session_state.patients):
            st.error("This Patient ID has already been entered. Use a unique ID.")
        else:
            st.session_state.patients.append({
                "Patient ID": patient_id.strip(),
                "Patient Name": patient_name.strip(),
                "Visit Date": str(patient_date),
                "Department": department,
                "Priority": priority,
                "Waiting Time (minutes)": int(waiting_time)
            })
            st.success("Patient details added successfully.")

st.divider()
st.subheader("Entered Patient Records")

if st.session_state.patients:
    df = pd.DataFrame(st.session_state.patients)
    st.dataframe(df, use_container_width=True, hide_index=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Remove All Records"):
            st.session_state.patients = []
            st.rerun()
    with col_b:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Patient Data (CSV)",
            data=csv_data,
            file_name="hospital_patient_data.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("Statistical Analysis and Report")

    times = df["Waiting Time (minutes)"]
    avg_time = float(times.mean())
    median_time = float(times.median())
    min_time = int(times.min())
    max_time = int(times.max())
    std_time = float(times.std()) if len(times) > 1 else 0.0
    variance = float(times.var()) if len(times) > 1 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Patients", len(df))
    m2.metric("Average Wait", f"{avg_time:.1f} min")
    m3.metric("Shortest Wait", f"{min_time} min")
    m4.metric("Longest Wait", f"{max_time} min")

    chart1, chart2 = st.columns(2)
    with chart1:
        st.write("**Waiting Time Distribution**")
        fig, ax = plt.subplots()
        ax.hist(times, bins=min(10, max(1, len(df))))
        ax.set_xlabel("Waiting time (minutes)")
        ax.set_ylabel("Number of patients")
        ax.set_title("Distribution of Patient Waiting Times")
        st.pyplot(fig)
        plt.close(fig)

    with chart2:
        st.write("**Average Waiting Time by Department**")
        dept_avg = df.groupby("Department")["Waiting Time (minutes)"].mean().sort_values()
        fig, ax = plt.subplots()
        dept_avg.plot(kind="bar", ax=ax)
        ax.set_xlabel("Department")
        ax.set_ylabel("Average waiting time (minutes)")
        ax.set_title("Department-wise Average Waiting Time")
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    dept_summary = (
        df.groupby("Department")["Waiting Time (minutes)"]
        .agg(["count", "mean", "min", "max"])
        .reset_index()
        .rename(columns={
            "count": "Patient Count",
            "mean": "Average Wait (minutes)",
            "min": "Minimum Wait (minutes)",
            "max": "Maximum Wait (minutes)"
        })
    )
    dept_summary["Average Wait (minutes)"] = dept_summary["Average Wait (minutes)"].round(2)
    st.write("**Department Summary**")
    st.dataframe(dept_summary, use_container_width=True, hide_index=True)

    priority_summary = (
        df.groupby("Priority")["Waiting Time (minutes)"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={
            "count": "Patient Count",
            "mean": "Average Wait (minutes)"
        })
    )
    priority_summary["Average Wait (minutes)"] = priority_summary["Average Wait (minutes)"].round(2)
    st.write("**Priority Summary**")
    st.dataframe(priority_summary, use_container_width=True, hide_index=True)

    longest_dept = dept_summary.loc[
        dept_summary["Average Wait (minutes)"].idxmax(), "Department"
    ]
    longest_dept_avg = dept_summary["Average Wait (minutes)"].max()
    report_lines = [
        "HOSPITAL PATIENT WAITING TIME ANALYSIS REPORT",
        "=" * 48,
        f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Number of patient records analyzed: {len(df)}",
        "",
        "OVERALL STATISTICS",
        f"Average waiting time: {avg_time:.2f} minutes",
        f"Median waiting time: {median_time:.2f} minutes",
        f"Minimum waiting time: {min_time} minutes",
        f"Maximum waiting time: {max_time} minutes",
        f"Standard deviation: {std_time:.2f} minutes",
        f"Variance: {variance:.2f}",
        "",
        "DEPARTMENT SUMMARY",
    ]
    for _, row in dept_summary.iterrows():
        report_lines.append(
            f"{row['Department']}: {int(row['Patient Count'])} patient(s), "
            f"average {row['Average Wait (minutes)']:.2f} minutes, "
            f"minimum {int(row['Minimum Wait (minutes)'])} minutes, "
            f"maximum {int(row['Maximum Wait (minutes)'])} minutes"
        )
    report_lines += [
        "",
        "OBSERVATION",
        f"{longest_dept} has the highest average waiting time "
        f"({longest_dept_avg:.2f} minutes) among the departments in the entered data.",
        "Review department staffing and patient flow to identify possible delays.",
        "",
        "Note: This report summarizes only the records entered by the user. "
        "It does not replace clinical judgment or hospital operational review."
    ]
    report_text = "\n".join(report_lines)

    st.text_area("Generated Report", report_text, height=300)
    st.download_button(
        "Download Analysis Report (TXT)",
        data=report_text.encode("utf-8"),
        file_name="hospital_waiting_time_report.txt",
        mime="text/plain"
    )

    st.caption("Privacy note: This demo keeps records in the current app session. Avoid entering real patient-identifying or confidential medical information.")
else:
    st.info("No patient records yet. Fill in the form above and click **Add Patient**. The report will appear after you add at least one patient.")
