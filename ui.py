import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🏆 Confluent Challenge: Topic Factory + Explorer")

tab1, tab2 = st.tabs(["🚀 Create", "🔍 Explore"])

with tab1:
    st.header("Create Topic")
    name = st.text_input("Topic Name", "bank-fraud-v1")
    partitions = st.slider("Partitions", 1, 24, 6)
    cluster_id = st.selectbox("Target Cluster", [1, 2], index=0)

    if st.button("CREATE TOPIC"):
        payload = {
            "name": name,
            "partitions": partitions,
            "cluster_id": cluster_id
        }
        resp = requests.post("http://localhost:8000/create-topic", json=payload)
        ...

        if resp.status_code == 200:
            st.success("✅ CREATED!")
            st.json(resp.json())
        else:
            st.error(resp.text)

with tab2:
    search = st.text_input("Search Topics")
    if st.button("🔎 SEARCH MULTI‑CLUSTER"):
        try:
            resp = requests.get("http://localhost:8000/list-topics", params={"search": search})
            data = resp.json()["topics"]
            
            # New format support
            topics_flat = []
            for item in data:
                if "topic" in item:
                    topics_flat.append(f"{item['cluster']}: {item['topic']}")
                else:
                    topics_flat.append(f"{item['cluster']}: Error - {item.get('error', 'unknown')}")
            
            st.success(f"Found {len(topics_flat)} across {len(set(item['cluster'] for item in data if 'cluster' in item))} clusters")
            st.text("\n".join(topics_flat[:20]))  # List view
        except Exception as e:
            st.error(f"Streamlit error: {str(e)}")

    
    st.caption("Multi‑cluster: Add cluster config → Loop AdminClient.list_topics()")
