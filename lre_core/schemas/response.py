from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ActiveLink(BaseModel):
    source_type: str = Field(..., description="'input' | 'concept'")
    source_id: str = Field(..., description="ID источника (например, 'x_width' или 'Z_OVERSIZE_WIDTH')")
    source_label: str = Field(..., description="Понятное имя источника")
    target_type: str = Field(..., description="'concept' | 'requirement'")
    target_id: str = Field(..., description="ID приемника (например, 'TR-03')")
    target_label: str = Field(..., description="Понятное имя приемника")
    weight: float = Field(..., description="Вес связи")
    contribution: float = Field(..., description="Вклад (активация * вес)")

class GraphTrace(BaseModel):
    trace_id: str = Field(..., description="Уникальный идентификатор трассировки")
    request_id: Optional[str] = Field(None, description="ID запроса КИС2")
    input_signals: Dict[str, float] = Field(..., description="Нормализованные входные сигналы слоя X")
    concept_activations: Dict[str, float] = Field(..., description="Активации концептуальных нейронов Z [0..1]")
    requirement_activations: Dict[str, float] = Field(..., description="Сырые вероятности требований Y [0..1]")
    active_links: List[ActiveLink] = Field(default_factory=list, description="Активные связи с существенным вкладом")

class RequirementItem(BaseModel):
    id: str = Field(..., description="ID требования из реестра (TR-01, KR-01 и т.д.)")
    area: str = Field(..., description="Категория/область (Транспорт, Крепление, Погрузка и т.д.)")
    name: str = Field(..., description="Наименование требования")
    status: str = Field("REQUIRED", description="'REQUIRED' | 'RECOMMENDED' | 'OPTIONAL'")
    probability: float = Field(..., ge=0.0, le=1.0, description="Оценка уверенности / вероятность")
    source: str = Field(..., description="'RULE_ENGINE' | 'NEURAL_CORE' | 'HYBRID'")
    rationale: str = Field(..., description="Понятное человеку объяснение причины формирования требования")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Конкретные параметры требования")

class RequirementInferenceResponse(BaseModel):
    request_id: Optional[str] = Field(None, description="ID запроса КИС2")
    status: str = Field("SUCCESS", description="Статус обработки")
    inference_timestamp: str = Field(..., description="ISO 8601 время генерации")
    trace_id: str = Field(..., description="ID трассировки для визуализатора")
    total_requirements: int = Field(..., description="Количество сформированных требований")
    requirements: List[RequirementItem] = Field(default_factory=list, description="Список требований")
    trace_summary: Optional[Dict[str, Any]] = Field(None, description="Краткая сводка активаций для быстрой справки")

class FeedbackPayload(BaseModel):
    trace_id: str
    request_id: Optional[str] = None
    accepted_requirements: List[str] = Field(default_factory=list, description="Список ID принятых логистом требований")
    rejected_requirements: List[str] = Field(default_factory=list, description="Список ID отклоненных логистом требований")
    added_requirements: List[str] = Field(default_factory=list, description="Список ID требований, добавленных вручную")
    comment: Optional[str] = None
