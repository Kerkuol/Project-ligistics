"""
Интерпретируемая концептуально-семантическая нейросеть (Concept-Bottleneck Network).
Реализация на чистом NumPy:
1. Быстрый инференс прямого распространения (<2 мс);
2. 100% интерпретируемость: каждый скрытый нейрон Z - это конкретное логистическое понятие;
3. Cold Start: веса инициализируются экспертной матрицей связей (Knowledge Priors);
4. Извлечение трассировки связей и вкладов (Trace Graph) для визуализатора.
"""
from typing import Dict, List, Tuple, Any
import numpy as np

from .registry import (
    INPUT_SIGNALS, INPUT_INDEX,
    CONCEPT_KEYS, CONCEPT_INDEX, CONCEPTS_REGISTRY,
    REQUIREMENT_KEYS, REQUIREMENT_INDEX, REQUIREMENTS_REGISTRY
)
from ..schemas.response import ActiveLink

class ConceptBottleneckNet:
    def __init__(self):
        self.num_inputs = len(INPUT_SIGNALS)
        self.num_concepts = len(CONCEPT_KEYS)
        self.num_requirements = len(REQUIREMENT_KEYS)
        
        # Матрицы весов
        # W_xz: (num_inputs, num_concepts)
        self.W_xz = np.zeros((self.num_inputs, self.num_concepts), dtype=np.float32)
        # W_zy: (num_concepts, num_requirements)
        self.W_zy = np.zeros((self.num_concepts, self.num_requirements), dtype=np.float32)
        
        # Смещения (biases)
        self.bias_z = np.full(self.num_concepts, -1.0, dtype=np.float32)
        self.bias_y = np.full(self.num_requirements, -1.5, dtype=np.float32)
        
        self._init_expert_priors()

    def _init_expert_priors(self):
        """
        Инициализация экспертных связей (Knowledge Priors) для холодного старта без датасета.
        """
        def link_xz(inp: str, concept: str, weight: float):
            i = INPUT_INDEX[inp]
            j = CONCEPT_INDEX[concept]
            self.W_xz[i, j] = weight

        def link_zy(concept: str, req: str, weight: float):
            j = CONCEPT_INDEX[concept]
            k = REQUIREMENT_INDEX[req]
            self.W_zy[j, k] = weight

        # 1. Связи Входы X -> Концепты Z
        link_xz("x_dim_width", "Z_OVERSIZE_WIDTH", 4.0)
        link_xz("x_dim_height", "Z_OVERSIZE_HEIGHT", 4.0)
        link_xz("x_dim_length", "Z_OVERSIZE_LENGTH", 4.0)
        
        link_xz("x_weight_single", "Z_HEAVY_AXLE_LOAD", 3.0)
        link_xz("x_weight_heavy_flag", "Z_HEAVY_AXLE_LOAD", 2.0)
        link_xz("x_weight_single", "Z_CRANE_RIGGING_COMPLEXITY", 3.0)
        
        link_xz("x_dim_height", "Z_DYNAMIC_INSTABILITY", 2.5)
        link_xz("x_weight_single", "Z_DYNAMIC_INSTABILITY", 2.0)
        
        link_xz("x_text_no_tilt", "Z_FRAGILITY_SENSITIVITY", 4.5)
        link_xz("x_non_stackable", "Z_FRAGILITY_SENSITIVITY", 1.5)
        
        link_xz("x_text_moisture_protect", "Z_WEATHER_CORROSION_RISK", 4.5)
        
        link_xz("x_high_cost", "Z_CARGO_HIGH_VALUE_RISK", 4.0)
        
        link_xz("x_text_direct_only", "Z_TRANSSHIPMENT_PROHIBITED", 4.5)
        link_xz("x_high_cost", "Z_TRANSSHIPMENT_PROHIBITED", 1.5)
        
        link_xz("x_text_crane_top", "Z_CRANE_RIGGING_COMPLEXITY", 4.0)
        
        link_xz("x_danger_hazard", "Z_HAZARDOUS_COMPLIANCE", 5.0)
        link_xz("x_danger_vet_kfk_skk", "Z_CUSTOMS_BORDER_FRICTION", 4.5)
        link_xz("x_incoterms_exw_fca", "Z_CUSTOMS_BORDER_FRICTION", 1.5)

        # 2. Связи Концепты Z -> Выходные требования Y
        # Негабарит по ширине
        link_zy("Z_OVERSIZE_WIDTH", "TR-03", 3.5) # Спецтранспорт
        link_zy("Z_OVERSIZE_WIDTH", "MR-03", 4.0) # Спецразрешение
        link_zy("Z_OVERSIZE_WIDTH", "MR-02", 3.0) # Ограничения маршрута
        link_zy("Z_OVERSIZE_WIDTH", "TR-04", 2.5) # Требования к ТС (уширители)

        # Негабарит по высоте
        link_zy("Z_OVERSIZE_HEIGHT", "TR-03", 3.5) # Низкорамный трал
        link_zy("Z_OVERSIZE_HEIGHT", "MR-03", 3.5) # Спецразрешение
        link_zy("Z_OVERSIZE_HEIGHT", "MR-02", 3.0) # Мосты / ЛЭП

        # Негабарит по длине
        link_zy("Z_OVERSIZE_LENGTH", "TR-03", 3.5) # Раздвижной трал
        link_zy("Z_OVERSIZE_LENGTH", "MR-03", 3.5) # Спецразрешение
        link_zy("Z_OVERSIZE_LENGTH", "MR-02", 2.5)

        # Тяжеловес / Осевые нагрузки
        link_zy("Z_HEAVY_AXLE_LOAD", "TR-03", 3.0) # Многоосный трал
        link_zy("Z_HEAVY_AXLE_LOAD", "KR-01", 3.5) # Спецкрепление
        link_zy("Z_HEAVY_AXLE_LOAD", "KR-02", 2.5) # Способ крепления (цепи)
        link_zy("Z_HEAVY_AXLE_LOAD", "KR-03", 2.5) # Параметры крепления
        link_zy("Z_HEAVY_AXLE_LOAD", "MR-03", 3.0) # Спецразрешение

        # Динамическая неустойчивость (центр тяжести)
        link_zy("Z_DYNAMIC_INSTABILITY", "DC-03", 4.0) # Данные о центре тяжести
        link_zy("Z_DYNAMIC_INSTABILITY", "KR-01", 2.5) # Спецкрепление
        link_zy("Z_DYNAMIC_INSTABILITY", "TR-10", 2.5) # Способ размещения

        # Хрупкость / Кантование
        link_zy("Z_FRAGILITY_SENSITIVITY", "TR-11", 3.5) # Особые условия размещения
        link_zy("Z_FRAGILITY_SENSITIVITY", "KR-01", 2.5) # Спецкрепление
        link_zy("Z_FRAGILITY_SENSITIVITY", "TR-07", 2.5) # Прямой транспорт
        link_zy("Z_FRAGILITY_SENSITIVITY", "TR-08", -4.0) # Перегруз (запрещен!)
        link_zy("Z_FRAGILITY_SENSITIVITY", "AD-03", -3.5) # Перевалка (запрещена!)

        # Влагозащита / Коррозия
        link_zy("Z_WEATHER_CORROSION_RISK", "TR-06", 3.0) # Размещение в закрытом кузове
        link_zy("Z_WEATHER_CORROSION_RISK", "WH-01", 2.5) # Временное хранение в сухом складе
        link_zy("Z_WEATHER_CORROSION_RISK", "TR-11", 2.5) # Особые условия (тент/чехол)

        # Высокая стоимость
        link_zy("Z_CARGO_HIGH_VALUE_RISK", "ST-01", 4.0) # Страхование груза
        link_zy("Z_CARGO_HIGH_VALUE_RISK", "ST-02", 3.5) # Страховая сумма
        link_zy("Z_CARGO_HIGH_VALUE_RISK", "DC-04", 3.0) # Фотоматериалы до/после
        link_zy("Z_CARGO_HIGH_VALUE_RISK", "TR-07", 2.5) # Прямой транспорт

        # Запрет перевалки
        link_zy("Z_TRANSSHIPMENT_PROHIBITED", "TR-07", 4.5) # Прямой транспорт
        link_zy("Z_TRANSSHIPMENT_PROHIBITED", "TR-08", -4.5) # Перегруз запрещен
        link_zy("Z_TRANSSHIPMENT_PROHIBITED", "AD-03", -4.5) # Перевалка запрещена

        # Сложность ПРР / Краны
        link_zy("Z_CRANE_RIGGING_COMPLEXITY", "PG-01", 3.0) # Способ погрузки (верх/кран)
        link_zy("Z_CRANE_RIGGING_COMPLEXITY", "PG-02", 3.0) # Способ выгрузки
        link_zy("Z_CRANE_RIGGING_COMPLEXITY", "PG-03", 4.5) # Погрузочное оборудование
        link_zy("Z_CRANE_RIGGING_COMPLEXITY", "DC-02", 2.5) # Чертежи строповки
        link_zy("Z_CRANE_RIGGING_COMPLEXITY", "PG-04", 2.5) # Условия площадки

        # Опасные грузы (ADR)
        link_zy("Z_HAZARDOUS_COMPLIANCE", "TR-02", 4.0) # Спецтранспорт ADR
        link_zy("Z_HAZARDOUS_COMPLIANCE", "DC-06", 4.0) # Разрешительные документы ADR/MSDS
        link_zy("Z_HAZARDOUS_COMPLIANCE", "MR-04", 3.0) # Условия прохождения границы

        # Таможня / Карантин
        link_zy("Z_CUSTOMS_BORDER_FRICTION", "DC-05", 4.0) # Сертификаты
        link_zy("Z_CUSTOMS_BORDER_FRICTION", "MR-05", 4.0) # Пограничный переход
        link_zy("Z_CUSTOMS_BORDER_FRICTION", "TM-02", 4.0) # Спец СВХ
        link_zy("Z_CUSTOMS_BORDER_FRICTION", "TM-03", 3.0) # Транзитные документы
        link_zy("Z_CUSTOMS_BORDER_FRICTION", "DC-07", 3.0) # Экспортные документы

    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))

    def forward(
        self,
        x_vector: np.ndarray,
        hard_rules_mask: Dict[str, float] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[ActiveLink]]:
        """
        Прямой ход сети:
        X -> Z (концепты) -> Y (требования).
        Возвращает:
        (z_scores, y_scores, active_links)
        """
        # 1. Вычисление активаций слоя понятий Z
        z_logits = np.dot(x_vector, self.W_xz) + self.bias_z
        z_scores = self.sigmoid(z_logits)

        # 2. Вычисление активаций требований Y
        y_logits = np.dot(z_scores, self.W_zy) + self.bias_y

        # 3. Инъекция жестких правил (если правило сработало, принудительный bias)
        if hard_rules_mask:
            mask_vector = np.array([hard_rules_mask.get(k, 0.0) for k in REQUIREMENT_KEYS], dtype=np.float32)
            y_logits += mask_vector * 10.0

        y_scores = self.sigmoid(y_logits)

        # 4. Сбор активных связей (для интерактивной визуализации графа)
        active_links: List[ActiveLink] = []

        # Связи X -> Z
        for i, x_val in enumerate(x_vector):
            if x_val > 0.05:
                for j, z_val in enumerate(z_scores):
                    weight = float(self.W_xz[i, j])
                    contribution = float(x_val * weight)
                    if abs(contribution) >= 0.25:
                        active_links.append(ActiveLink(
                            source_type="input",
                            source_id=INPUT_SIGNALS[i],
                            source_label=INPUT_SIGNALS[i].replace("x_", ""),
                            target_type="concept",
                            target_id=CONCEPT_KEYS[j],
                            target_label=CONCEPTS_REGISTRY[CONCEPT_KEYS[j]]["name"],
                            weight=round(weight, 2),
                            contribution=round(contribution, 3)
                        ))

        # Связи Z -> Y
        for j, z_val in enumerate(z_scores):
            if z_val > 0.15:
                for k, y_val in enumerate(y_scores):
                    weight = float(self.W_zy[j, k])
                    contribution = float(z_val * weight)
                    if abs(contribution) >= 0.25:
                        req_id = REQUIREMENT_KEYS[k]
                        active_links.append(ActiveLink(
                            source_type="concept",
                            source_id=CONCEPT_KEYS[j],
                            source_label=CONCEPTS_REGISTRY[CONCEPT_KEYS[j]]["name"],
                            target_type="requirement",
                            target_id=req_id,
                            target_label=f"{req_id} {REQUIREMENTS_REGISTRY[req_id]['name']}",
                            weight=round(weight, 2),
                            contribution=round(contribution, 3)
                        ))

        return z_scores, y_scores, active_links
