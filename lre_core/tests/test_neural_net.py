import pytest
import numpy as np
from lre_core.engine.neural_net import ConceptBottleneckNet
from lre_core.engine.registry import (
    INPUT_SIGNALS, INPUT_INDEX,
    CONCEPT_KEYS, CONCEPT_INDEX,
    REQUIREMENT_KEYS, REQUIREMENT_INDEX
)

def test_neural_net_dimensions_and_ranges():
    net = ConceptBottleneckNet()
    x = np.zeros(len(INPUT_SIGNALS), dtype=np.float32)
    z_scores, y_scores, active_links = net.forward(x)
    
    assert len(z_scores) == len(CONCEPT_KEYS)
    assert len(y_scores) == len(REQUIREMENT_KEYS)
    assert np.all(z_scores >= 0.0) and np.all(z_scores <= 1.0)
    assert np.all(y_scores >= 0.0) and np.all(y_scores <= 1.0)

def test_oversize_input_activates_concept_and_requirements():
    net = ConceptBottleneckNet()
    x = np.zeros(len(INPUT_SIGNALS), dtype=np.float32)
    # Подаем сильный сигнал негабаритной ширины
    x[INPUT_INDEX["x_dim_width"]] = 1.8
    
    z_scores, y_scores, active_links = net.forward(x)
    
    # Нейрон негабарита по ширине должен активироваться
    z_idx = CONCEPT_INDEX["Z_OVERSIZE_WIDTH"]
    assert z_scores[z_idx] > 0.8
    
    # Требования к спецтранспорту (TR-03) и спецразрешению (MR-03) должны вырасти
    assert y_scores[REQUIREMENT_INDEX["TR-03"]] > 0.7
    assert y_scores[REQUIREMENT_INDEX["MR-03"]] > 0.7
    
    # В активных связях должна присутствовать цепочка
    has_input_link = any(
        l.source_id == "x_dim_width" and l.target_id == "Z_OVERSIZE_WIDTH"
        for l in active_links
    )
    has_concept_link = any(
        l.source_id == "Z_OVERSIZE_WIDTH" and l.target_id == "TR-03"
        for l in active_links
    )
    assert has_input_link is True
    assert has_concept_link is True

def test_hard_rule_mask_guarantees_activation():
    net = ConceptBottleneckNet()
    x = np.zeros(len(INPUT_SIGNALS), dtype=np.float32)
    # Жесткое правило требует DC-03 (центр тяжести)
    hard_mask = {"DC-03": 1.0}
    
    _, y_scores, _ = net.forward(x, hard_rules_mask=hard_mask)
    assert y_scores[REQUIREMENT_INDEX["DC-03"]] > 0.99
