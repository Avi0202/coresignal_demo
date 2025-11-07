import streamlit as st
import requests
import pandas as pd
import csv
import json

# -----------------------
# CONFIG
# -----------------------
API_KEY = "LJf8CqR5d2K0C8Tv1ys0K3tbVKrvaWXp"
SEARCH_URL = "https://api.coresignal.com/cdapi/v2/job_multi_source/search/es_dsl"
COLLECT_URL = "https://api.coresignal.com/cdapi/v2/job_multi_source/collect"

st.set_page_config(page_title="Coresignal Jobs Explorer", layout="wide")

# -----------------------
# UI HEADER
# -----------------------
st.title("💼 Coresignal Multi-source Jobs Explorer")
st.caption("Search, explore, and analyze jobs from multiple sources using Coresignal’s API")

# -----------------------
# SIDEBAR FILTERS
# -----------------------
with st.sidebar:
    st.header("🔍 Search Criteria")
    search_term = st.text_input("Keyword / Job Title", value="Software Engineer")
    location = st.text_input("Location", value="Bangalore")
    country = st.text_input("Country", value="India")
    limit = st.number_input("Number of results to fetch", min_value=1, max_value=100, value=20)
    run_search = st.button("🚀 Search Jobs")

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def search_jobs(location, country, keyword, limit):
    """
    Uses the /search/es_dsl endpoint to return job IDs matching the filters.
    """
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }

    # ✅ Minimal ES DSL body that Coresignal expects
    body = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"location": location}},
                    {"match": {"city": location}},
                    {"match": {"country": country}},
                    {"match": {"title": keyword}}
                ]
            }
        }
    }

    with st.spinner("🔍 Searching for jobs..."):
        resp = requests.post(SEARCH_URL, headers=headers, json=body, timeout=60)

    if resp.status_code == 200:
        job_ids = resp.json()
        if not job_ids:
            st.warning("No matching jobs found.")
        return job_ids[:limit]
    else:
        st.error(f"⚠️ API Error {resp.status_code}: {resp.text}")
        return []


def get_job_details(job_id):
    """
    Fetches full job detail for a given job_id using /collect/{id}.
    """
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    url = f"{COLLECT_URL}/{job_id}"

    with st.spinner(f"Fetching job details for ID {job_id}..."):
        resp = requests.get(url, headers=headers, timeout=60)

    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"❌ Failed to fetch job {job_id}: {resp.status_code}")
        return None


# -----------------------
# MAIN LOGIC
# -----------------------
if run_search:
    job_ids = search_jobs(location, country, search_term, limit)

    if job_ids:
        st.success(f"✅ Found {len(job_ids)} matching job(s)")
        st.dataframe(pd.DataFrame({"Job IDs": job_ids}))

        st.divider()
        st.subheader("📋 Select a Job ID to View Details")
        selected_id = st.selectbox("Select Job ID", job_ids)

        if st.button("🧩 Get Job Details"):
            job_data = get_job_details(selected_id)
            if job_data:
                # Display key details
                st.subheader(f"🏢 {job_data.get('company_name', 'Unknown')} — {job_data.get('title', '')}")
                st.caption(f"📍 {job_data.get('location', 'N/A')}")
                st.markdown(f"**Industry:** {job_data.get('company_industry', 'N/A')}  \n"
                            f"**Employment Type:** {job_data.get('employment_type', 'N/A')}  \n"
                            f"**Seniority:** {job_data.get('seniority', 'N/A')}")

                # Description
                with st.expander("📄 Job Description"):
                    st.write(job_data.get("description", "No description available."))

                # Salary
                salary = job_data.get("salary", [])
                if salary:
                    st.markdown("💰 **Salary Info:**")
                    for s in salary:
                        st.markdown(f"- {s.get('text')} ({s.get('currency')})")
                else:
                    st.markdown("💰 No salary data available.")

                # Technologies
                techs = job_data.get("company_technologies", [])
                if techs:
                    st.markdown("🧠 **Technologies Used:**")
                    st.write(", ".join([t["technology"] for t in techs]))
                else:
                    st.markdown("🧠 No tech stack info available.")

                # Benefits
                benefits = job_data.get("benefits", [])
                if benefits:
                    st.markdown("🎁 **Benefits:**")
                    st.write(", ".join(benefits))

                # Full JSON
                with st.expander("🧾 Full JSON Response"):
                    st.json(job_data)

                # Convert to CSV
                df = pd.json_normalize(job_data)
                csv_data = df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)
                st.download_button(
                    label="📥 Download Job Details (CSV)",
                    data=csv_data,
                    file_name=f"job_{selected_id}.csv",
                    mime="text/csv"
                )
else:
    st.info("👈 Use the sidebar to search for jobs.")
