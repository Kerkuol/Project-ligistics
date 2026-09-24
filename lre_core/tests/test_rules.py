import pytest
from lre_core.schemas.request import TransportRequest, CargoInfo, CargoDimensions, CargoDanger, Location
from lre_core.engine.rules import RuleEngine

def create_sample_request(width=2.4, height=2.4, length=12.0, weight_kg=5000, imo=None, un=None):
    return TransportRequest(
        request_id="REQ-TEST-01",
        origin=Location(country="РФ", city="Москва"),
        destination=Location(country="РФ", city="Казань"),
        cargo=CargoInfo(
            name="Тестовый груз",
            dimensions=CargoDimensions(
                length_m=length,
                width_m=width,
                height_m=height,
                weight_kg=weight_kg,
                places_count=1
            ),
            danger=CargoDanger(imo=imo, un=un)
        )
    )

def test_standard_cargo_no_oversize():
    engine = RuleEngine()
    req = create_sample_request(width=2.4, height=2.4, length=12.0, weight_kg=1200)
    res = engine.evaluate(req)
    
    assert res.flags["is_oversize_width"] is False
    assert res.flags["is_high_cargo"] is False
    assert res.flags["is_heavy_single_piece"] is False
    assert res.hard_rule_mask["TR-03"] == 0.0
    assert res.hard_rule_mask["MR-03"] == 0.0

def test_oversize_width_triggers_special_vehicle_and_permit():
    engine = RuleEngine()
    req = create_sample_request(width=3.2, height=2.4, length=12.0, weight_kg=5000)
    res = engine.evaluate(req)
    
    assert res.flags["is_oversize_width"] is True
    assert res.hard_rule_mask["TR-03"] == 1.0 # Спецтранспорт
    assert res.hard_rule_mask["MR-03"] == 1.0 # Спецразрешение
    assert "Ширина" in res.rationales["TR-03"]

def test_heavy_cargo_triggers_crane_and_lashing():
    engine = RuleEngine()
    req = create_sample_request(weight_kg=18500)
    res = engine.evaluate(req)
    
    assert res.flags["is_heavy_single_piece"] is True
    assert res.hard_rule_mask["KR-01"] == 1.0 # Спецкрепление
    assert res.hard_rule_mask["PG-03"] == 1.0 # Погрузочное оборудование
    assert "18.50 т" in res.rationales["KR-01"]

def test_dangerous_cargo_triggers_adr():
    engine = RuleEngine()
    req = create_sample_request(imo="3", un="1203")
    res = engine.evaluate(req)
    
    assert res.flags["has_danger"] is True
    assert res.hard_rule_mask["TR-02"] == 1.0
    assert res.hard_rule_mask["DC-06"] == 1.0
