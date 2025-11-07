import streamlit as st
import requests
import pandas as pd
import csv

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
    limit = st.number_input("Number of results to fetch", min_value=1, max_value=50, value=10)
    run_search = st.button("🚀 Search Jobs")

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def search_jobs(location, country, keyword, limit):
    headers = {"Content-Type": "application/json", "apikey": API_KEY}
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
        return job_ids[:limit]
    else:
        st.error(f"⚠️ API Error {resp.status_code}: {resp.text}")
        return []


def get_job_details(job_id):
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    url = f"{COLLECT_URL}/{job_id}"
    resp = requests.get(url, headers=headers, timeout=60)
    if resp.status_code == 200:
        return resp.json()
    return None


# -----------------------
# MAIN LOGIC
# -----------------------
if run_search:
    job_ids = search_jobs(location, country, search_term, limit)

    if job_ids:
        all_jobs = []
        st.info(f"🔎 Found {len(job_ids)} jobs. Fetching details...")
        progress = st.progress(0)

        for i, job_id in enumerate(job_ids, start=1):
            job_data = get_job_details(job_id)
            if job_data:
                all_jobs.append({
                    "Title": job_data.get("title", ""),
                    "Company": job_data.get("company_name", ""),
                    "Location": job_data.get("location", ""),
                    "Country": job_data.get("country", ""),
                    "Employment Type": job_data.get("employment_type", ""),
                    "Seniority": job_data.get("seniority", ""),
                    "Industry": job_data.get("company_industry", ""),
                    "Description": job_data.get("description", "")[:200]  # short preview
                })
            progress.progress(i / len(job_ids))

        if all_jobs:
            df = pd.DataFrame(all_jobs)
            st.success("✅ Job details fetched successfully!")
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)
            st.download_button(
                label="📥 Download All Jobs (CSV)",
                data=csv_data,
                file_name="all_jobs.csv",
                mime="text/csv"
            )
        else:
            st.warning("No job details found.")
    else:
        st.warning("No matching jobs found.")
else:
    st.info("👈 Use the sidebar to search for jobs.")

