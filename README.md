**Title**: Properties‑Driven Multi‑Cluster Kafka Topic Factory

**Description**: 
Create + search topics across clusters using **client.properties** config. 
No hardcode—scales to N clusters from file/Excel.

**Demo Video**: <>

**Live Console**: 
- AWS: pkc-921jm (topics: rollback-test_win, bank-fraud-v1)
- GCP: pkc-619z3 (win_challenge_Cluster_1)

**Features**:
- Multi‑cluster AdminClient loop
- Custom partitions/retention
- Audit Producer
- Streamlit UI (create/search)

**Impact**: Production platform tool. 10x faster ops for banking fraud pipelines..

**Stack**: Confluent Cloud, Kafka AdminClient/Producer, properties config, Python

## Setup
1. `pip install fastapi uvicorn confluent-kafka streamlit pydantic`
2. Copy `client.properties.example` → `client.properties` (add your bootstrap/API keys)
3. `python challenge.py`
4. `streamlit run ui.py`
# theKafkaguy-confluent-challenge
