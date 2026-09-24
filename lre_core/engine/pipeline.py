"""
Сквозной пайплайн логического вывода (Pipeline Orchestrator).
Координирует:
RuleEngine -> SemanticTextParser -> ConceptBottleneckNet -> ParameterExtractor.
"""
import uuid
import datetime
from typing import Tuple, Dict, Any, List
import numpy as np

from ..schemas.request import TransportRequest
from ..schemas.response import (
    RequirementInferenceResponse, RequirementItem, GraphTrace, ActiveLink
)
from .registry import (
    INPUT_SIGNALS, INPUT_INDEX,
    CONCEPT_KEYS, CONCEPTS_REGISTRY,
    REQUIREMENT_KEYS, REQUIREMENTS_REGISTRY
)
from .rules import RuleEngine, RuleCheckResult
from .nlp import SemanticTextParser
from .neural_net import ConceptBottleneckNet
from .parameters import ParameterExtractor
from ..config import settings

class InferencePipeline:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.nlp_parser = SemanticTextParser()
        self.neural_net = ConceptBottleneckNet()
        self.param_extractor = ParameterExtractor()

    def _build_input_vector(self, request: TransportRequest, rules: RuleCheckResult, nlp_signals: Dict[str, float]) -> np.ndarray:
        """
        Преобразует данные запроса и текстовые сигналы в нормализованный вектор X.
        """
        x = np.zeros(len(INPUT_SIGNALS), dtype=np.float32)
        dims = request.cargo.dimensions
        
        # Габариты: нормализация относительно стандартов
        # 1. Ширина (> 2.55м)
        if dims.width_m > 2.55:
            x[INPUT_INDEX["x_dim_width"]] = min(2.0, (dims.width_m - 2.55) / 0.5 + 1.0)
            
        # 2. Высота (> 2.80м)
        if dims.height_m > 2.80:
            x[INPUT_INDEX["x_dim_height"]] = min(2.0, (dims.height_m - 2.80) / 0.5 + 1.0)
            
        # 3. Длина (> 13.6м)
        if dims.length_m > 13.6:
            x[INPUT_INDEX["x_dim_length"]] = min(2.0, (dims.length_m - 13.6) / 2.0 + 1.0)
            
        # 4. Вес неделимого места (> 1.5 т, шкала до 30 т)
        weight_tons = dims.weight_kg / 1000.0
        if weight_tons >= 1.5:
            x[INPUT_INDEX["x_weight_single"]] = min(2.0, weight_tons / 15.0)
            x[INPUT_INDEX["x_weight_heavy_flag"]] = 1.0
            
        # 5. Общий вес
        tot_weight_tons = (dims.total_weight_kg or (dims.weight_kg * dims.places_count)) / 1000.0
        if tot_weight_tons > 20.0:
            x[INPUT_INDEX["x_total_weight"]] = min(2.0, tot_weight_tons / 25.0)
            
        # 6. Стоимость груза (> 50k USD)
        cost_val = request.cargo.cost.value if request.cargo.cost and request.cargo.cost.value else 0.0
        if cost_val >= 50000.0:
            x[INPUT_INDEX["x_high_cost"]] = min(2.0, cost_val / 100000.0)
            
        # 7. Опасность (IMO / UN)
        if request.cargo.danger.imo or request.cargo.danger.un:
            x[INPUT_INDEX["x_danger_hazard"]] = 1.0
            
        # 8. ВЕТ / СКК / КФК
        if request.cargo.danger.vet or request.cargo.danger.kfk or request.cargo.danger.skk:
            x[INPUT_INDEX["x_danger_vet_kfk_skk"]] = 1.0
            
        # 9. Штабелирование
        if not dims.stackable:
            x[INPUT_INDEX["x_non_stackable"]] = 1.0
            
        # 10. Текстовые NLP сигналы
        x[INPUT_INDEX["x_text_no_tilt"]] = nlp_signals.get("no_tilt", 0.0)
        x[INPUT_INDEX["x_text_crane_top"]] = nlp_signals.get("crane_top", 0.0)
        x[INPUT_INDEX["x_text_moisture_protect"]] = nlp_signals.get("moisture_protect", 0.0)
        x[INPUT_INDEX["x_text_direct_only"]] = nlp_signals.get("direct_only", 0.0)
        
        # 11. Incoterms
        inc = (request.incoterms or "").upper()
        if inc in ["EXW", "FCA"]:
            x[INPUT_INDEX["x_incoterms_exw_fca"]] = 1.0
            
        # 12. Мультимодал
        tr_mode = (request.primary_transport or "").lower()
        if "мульти" in tr_mode or "мор" in tr_mode:
            x[INPUT_INDEX["x_transport_multimodal"]] = 1.0
            
        return x

    def run(self, request: TransportRequest) -> Tuple[RequirementInferenceResponse, GraphTrace]:
        trace_id = f"trace-{uuid.uuid4().hex[:10]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Шаг 1: Детерминированные правила
        rule_result = self.rule_engine.evaluate(request)
        
        # Шаг 2: Семантический анализ текста
        nlp_signals = self.nlp_parser.parse(request)
        
        # Шаг 3: Формирование входного вектора X
        x_vector = self._build_input_vector(request, rule_result, nlp_signals)
        
        # Шаг 4: Прогон через нейросеть
        z_scores, y_scores, active_links = self.neural_net.forward(
            x_vector=x_vector,
            hard_rules_mask=rule_result.hard_rule_mask
        )
        
        # Шаг 5: Фильтрация и формирование списка требований
        requirements_list: List[RequirementItem] = []
        
        for k_idx, req_id in enumerate(REQUIREMENT_KEYS):
            prob = float(y_scores[k_idx])
            rule_bias = rule_result.hard_rule_mask.get(req_id, 0.0)
            
            # Требование включается, если сработало жесткое правило ИЛИ нейросеть превысила порог
            if rule_bias > 0.5 or prob >= settings.REQUIREMENT_ACTIVATION_THRESHOLD:
                reg_info = REQUIREMENTS_REGISTRY[req_id]
                
                # Определение источника и обоснования
                if rule_bias > 0.5 and req_id in rule_result.rationales:
                    source = "RULE_ENGINE"
                    rationale = rule_result.rationales[req_id]
                elif rule_bias > 0.5:
                    source = "RULE_ENGINE"
                    rationale = "Обязательное нормативное требование по правилам перевозок."
                else:
                    source = "NEURAL_CORE"
                    # Поиск наиболее повлиявшего концепта
                    contributing_concepts = []
                    for j_idx, c_key in enumerate(CONCEPT_KEYS):
                        w = self.neural_net.W_zy[j_idx, k_idx]
                        z_val = z_scores[j_idx]
                        if z_val * w > 0.3:
                            c_name = CONCEPTS_REGISTRY[c_key]["name"]
                            contributing_concepts.append(f"{c_name} (активация {z_val:.2f})")
                    if contributing_concepts:
                        rationale = f"Сформировано нейросетью на основе факторов: {', '.join(contributing_concepts)}."
                    else:
                        rationale = "Сформировано на основе совокупного анализа параметров перевозки."
                
                # Обогащение параметрами
                params = self.param_extractor.enrich(req_id, request, prob)
                
                requirements_list.append(RequirementItem(
                    id=req_id,
                    area=reg_info["area"],
                    name=reg_info["name"],
                    status="REQUIRED" if prob >= 0.7 else "RECOMMENDED",
                    probability=round(prob, 3),
                    source=source,
                    rationale=rationale,
                    parameters=params
                ))

        # Сортировка требований по важности / вероятности
        requirements_list.sort(key=lambda r: r.probability, reverse=True)

        # Шаг 6: Формирование структуры трассировки для визуализатора
        concept_dict = {
            CONCEPT_KEYS[j]: round(float(z_scores[j]), 3)
            for j in range(len(CONCEPT_KEYS))
        }
        requirement_dict = {
            REQUIREMENT_KEYS[k]: round(float(y_scores[k]), 3)
            for k in range(len(REQUIREMENT_KEYS))
        }
        input_dict = {
            INPUT_SIGNALS[i]: round(float(x_vector[i]), 3)
            for i in range(len(INPUT_SIGNALS))
        }
        
        graph_trace = GraphTrace(
            trace_id=trace_id,
            request_id=request.request_id,
            input_signals=input_dict,
            concept_activations=concept_dict,
            requirement_activations=requirement_dict,
            active_links=active_links
        )

        response = RequirementInferenceResponse(
            request_id=request.request_id,
            status="SUCCESS",
            inference_timestamp=timestamp,
            trace_id=trace_id,
            total_requirements=len(requirements_list),
            requirements=requirements_list,
            trace_summary={
                "active_concepts_count": sum(1 for v in z_scores if v >= settings.CONCEPT_ACTIVATION_THRESHOLD),
                "total_active_links": len(active_links)
            }
        )

        return response, graph_trace
