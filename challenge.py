from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
import json
import uvicorn

app = FastAPI()

def read_config():
    config = {}
    with open("client.properties") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                k, v = line.split('=', 1)
                config[k.strip()] = v.strip()
    config["sasl.mechanism"] = config.pop("sasl.mechanisms", "PLAIN")
    return config

def get_clusters(config):
    clusters = []
    i = 1
    while f"bootstrap.servers.{i}" in config:
        cluster = {
            "bootstrap.servers": config[f"bootstrap.servers.{i}"],
            "sasl.username": config[f"sasl.username.{i}"],
            "sasl.password": config[f"sasl.password.{i}"],
            "security.protocol": config["security.protocol"],
            "sasl.mechanism": config["sasl.mechanism"]
        }
        clusters.append(cluster)
        i += 1
    if not clusters:
        clusters = [config]  # Fallback single
    return clusters


config = read_config()
CLUSTERS = get_clusters(config)   # list of dicts, one per cluster


class TopicReq(BaseModel):
    name: str
    partitions: int = 6
    cluster_id: int = 1   # 1 = first cluster in client.properties

@app.post("/create-topic")
async def create_topic(req: TopicReq):
    cluster_index = max(1, min(req.cluster_id, len(CLUSTERS))) - 1
    cluster_conf = CLUSTERS[cluster_index]
    
    admin = AdminClient(cluster_conf)
    new_topic = NewTopic(
        req.name, 
        num_partitions=req.partitions,
        config={"retention.ms": "604800000"}
    )
    futures = admin.create_topics([new_topic])
    
    for topic, future in futures.items():
        future.result(timeout=60)
    
    p = Producer(cluster_conf)
    p.produce("audit-log", value=json.dumps({"topic": req.name, "cluster": cluster_index + 1}).encode('utf-8'))
    p.flush()
    
    return {"success": True, "topic": req.name, "cluster": cluster_index + 1}




@app.get("/list-topics")
async def list_topics(search: str = ""):
    all_topics = []
    for i, cluster_conf in enumerate(CLUSTERS):
        try:
            admin = AdminClient(cluster_conf)
            md = admin.list_topics(timeout=10)
            for topic_name in md.topics.keys():
                if not topic_name.startswith('_') and (not search or search.lower() in topic_name.lower()):
                    all_topics.append({"cluster": f"Cluster {i+1}", "topic": topic_name})
        except Exception as e:
            all_topics.append({"cluster": f"Cluster {i+1}", "error": str(e)})
    return {"topics": all_topics}


if __name__ == "__main__":
    print(f"Loaded {len(CLUSTERS)} clusters")
    uvicorn.run(app, host="0.0.0.0", port=8000)
