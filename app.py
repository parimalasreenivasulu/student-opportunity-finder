import streamlit as st
from datetime import date

from database import (
    initialize_database,
    get_opportunities,
    add_sample_opportunities,
    add_opportunity,
    update_opportunity_status,
)

st.set_page_config(page_title="Student Opportunity Finder", page_icon="📘", layout="wide")
add_sample_opportunities()

st.title("ðŸŽ“ Student Opportunity Finder")
st.caption("Discover internships, scholarships, free courses, certifications, and fresher jobs.")
st.info("DEMO VERSION: listings are sample records, not verified real openings. Check official provider websites.")
opportunities = get_opportunities(approved_only=True)
with st.sidebar:
    st.header("Find opportunities")
    search_text = st.text_input("Search by title, organization, or skill")
    categories = ["All", "Internship", "Scholarship", "Free Course", "Certification", "Fresher Job"]
    selected_category = st.selectbox("Category", categories)
    locations = ["All"] + sorted({x["location"] for x in opportunities})
    selected_location = st.selectbox("Location", locations)

today = date.today().isoformat()
filtered = []
for item in opportunities:
    if selected_category != "All" and item["category"] != selected_category:
        continue
    if selected_location != "All" and item["location"] != selected_location:
        continue
    searchable = " ".join(str(item.get(k) or "") for k in [
        "title", "organization", "description", "eligibility", "skills", "category", "location"
    ]).lower()
    if search_text.strip() and search_text.strip().lower() not in searchable:
        continue
    filtered.append(item)

a, b, c = st.columns(3)
a.metric("Listings shown", len(filtered))
b.metric("Categories shown", len({x["category"] for x in filtered}))
c.metric("Version", "Demo")
st.divider()

if not filtered:
    st.warning("No matching opportunities. Try another keyword or category.")
for item in filtered:
    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.subheader(item["title"])
            st.write(f'**{item["organization"]}** Â· {item["category"]} Â· {item["location"]}')
            st.write(item["description"])
            st.write(f'**Eligibility:** {item["eligibility"]}')
            st.write(f'**Skills/topics:** {item["skills"] or "Not specified"}')
            if item["deadline"]:
                if item["deadline"] < today:
                    st.warning(f'Sample deadline has passed: {item["deadline"]}')
                else:
                    st.write(f'**Deadline:** {item["deadline"]}')
            st.caption(f'Source: {item["source_url"]}')
            st.caption(f'Last checked: {item["last_verified"] or "Not checked"}')
        with right:
            st.write(f'**Status:** {item["status"]}')
            st.link_button("Open source", item["source_url"], use_container_width=True)

st.divider()
st.caption("Student Opportunity Finder Â· Python + Streamlit + SQLite")


st.divider()

st.header("Submit a New Opportunity")
st.write("Share an internship, scholarship, course, certification, or fresher job.")

with st.form("opportunity_submission_form"):
    title = st.text_input("Opportunity Title")

    category = st.selectbox(
        "Category",
        ["Internship", "Scholarship", "Free Course", "Certification", "Fresher Job"],
    )

    organization = st.text_input("Organization")
    description = st.text_area("Description")
    eligibility = st.text_area("Eligibility Requirements")
    location = st.text_input("Location", value="Online")
    deadline = st.date_input("Deadline (optional)", value=None)
    skills = st.text_input("Skills or Topics")
    source_url = st.text_input("Official Source URL")

    submitted = st.form_submit_button("Submit Opportunity")

    if submitted:
        item = {
            "title": title,
            "category": category,
            "organization": organization,
            "description": description,
            "eligibility": eligibility,
            "location": location,
            "deadline": deadline.isoformat() if deadline else None,
            "skills": skills,
            "source_url": source_url,
            "status": "PENDING REVIEW",
        }

        try:
            add_opportunity(item)
            st.success("Opportunity submitted successfully!")
            st.info("This submission is pending review.")
        except ValueError as error:
            st.error(f"Please check your submission: {error}")
        except Exception as error:
            st.error(f"Could not save the opportunity: {error}")
st.divider()

st.write("Review submitted opportunities before approving or rejecting them.")
import os
import hmac
st.divider()
st.header("Administrator Review")

import os
import hmac

admin_password = os.environ.get("STUDENT_FINDER_ADMIN_PASSWORD", "")

if not admin_password:
    st.warning(
        "Admin login is not configured. "
        "Set the STUDENT_FINDER_ADMIN_PASSWORD environment variable."
    )
    st.stop()

entered_password = st.text_input(
    "Administrator Password",
    type="password",
)

if not entered_password or not hmac.compare_digest(
    entered_password,
    admin_password,
):
    st.info("Enter the administrator password to access review controls.")
    st.stop()

st.success("Administrator authenticated.")

st.write("Review submitted opportunities before approving or rejecting them.")

all_opportunities = get_opportunities()

pending_opportunities = [
    item
    for item in all_opportunities
    if item["status"].strip().upper() == "PENDING REVIEW"
]

if not pending_opportunities:
    st.info("There are no pending submissions to review.")

for item in pending_opportunities:
    with st.container(border=True):
        st.subheader(item["title"])

        st.write(f"**Organization:** {item['organization']}")
        st.write(f"**Category:** {item['category']}")
        st.write(f"**Description:** {item['description']}")
        st.write(f"**Eligibility:** {item['eligibility']}")
        st.write(f"**Skills:** {item['skills'] or 'Not specified'}")
        st.write(f"**Source URL:** {item['source_url']}")
        st.write(f"**Status:** {item['status']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Approve",
                key=f"approve_{item['id']}",
                use_container_width=True,
            ):
                updated = update_opportunity_status(
                    item["id"], "APPROVED"
                )

                if updated:
                    st.success("Opportunity approved!")
                    st.rerun()
                else:
                    st.warning("This opportunity is no longer pending.")

        with col2:
            if st.button(
                "Reject",
                key=f"reject_{item['id']}",
                use_container_width=True,
            ):
                updated = update_opportunity_status(
                    item["id"], "REJECTED"
                )

                if updated:
                    st.success("Opportunity rejected.")
                    st.rerun()
                else:
                    st.warning("This opportunity is no longer pending.")