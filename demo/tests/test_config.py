import yaml, json, os

def test_pagination_reasonable():
    with open(os.path.join("config","app.yaml")) as f:
        cfg = yaml.safe_load(f)
    assert 1 <= cfg["pagination"] <= 100

def test_rollout_not_100_instantly():
    with open(os.path.join("flags","rollout.json")) as f:
        flags = json.load(f)
    assert flags["featureX"]["percentage"] <= 50
