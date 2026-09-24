import pytest
from fastapi.testclient import TestClient
from lre_core.app import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

def test_graph_schema():
    res = client.get("/v1/graph-schema")
    assert res.status_code == 200
    data = res.json()
    assert "inputs" in data
    assert "concepts" in data
    assert "requirements" in data
    assert len(data["concepts"]) == 12
    assert len(data["requirements"]) == 45

def test_e2e_complex_project_cargo():
    # Сложная проектная перевозка промышленного негабаритного агрегата
    payload = {
        "request_id": "REQ-PROJECT-889",
        "incoterms": "FCA",
        "origin": {
            "country": "Германия",
            "city": "Кёльн",
            "address": "Industriestrasse 10"
        },
        "destination": {
            "country": "Казахстан",
            "city": "Атырау",
            "address": "Промзона 4"
        },
        "cargo": {
            "name": "Промышленный модуль компрессорной станции",
            "danger": {
                "imo": None,
                "un": None,
                "vet": False,
                "skk": False,
                "kfk": False
            },
            "dimensions": {
                "length_m": 8.5,
                "width_m": 3.4,
                "height_m": 3.1,
                "weight_kg": 26000,
                "places_count": 1,
                "stackable": False,
                "heavy_single_place": True
            },
            "cost": {
                "value": 240000,
                "currency": "EUR"
            }
        },
        "primary_transport": "автомобильный",
        "notes": {
            "request_notes": "Срочный проект. Груз боится влаги, не кантовать!",
            "loading_notes": "Погрузка мостовым краном, заводской захват через верх.",
            "delivery_notes": "Выгрузка заказчиком на подготовленной площадке."
        }
    }

    res = client.post("/v1/requirements/infer", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["request_id"] == "REQ-PROJECT-889"
    assert data["total_requirements"] > 5
    
    req_ids = [r["id"] for r in data["requirements"]]
    
    # 1. Спецтранспорт и спецразрешение (Ширина 3.4м > 2.55м, высота 3.1м)
    assert "TR-03" in req_ids
    assert "MR-03" in req_ids
    
    # 2. Кран и крепление (Вес 26 т)
    assert "PG-03" in req_ids
    assert "KR-01" in req_ids
    
    # 3. Прямой транспорт (Хрупкость / не кантовать / высокая стоимость)
    assert "TR-07" in req_ids
    
    # 4. Проверяем параметры крана
    crane_req = next(r for r in data["requirements"] if r["id"] == "PG-03")
    assert crane_req["parameters"]["min_crane_capacity_tons"] >= 26.0 * 1.25

    # 5. Проверяем, что создалась трассировка
    trace_id = data["trace_id"]
    res_trace = client.get(f"/v1/traces/{trace_id}")
    assert res_trace.status_code == 200
    trace_data = res_trace.json()
    assert "concept_activations" in trace_data
    assert len(trace_data["active_links"]) > 0
