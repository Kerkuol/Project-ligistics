"""
FastAPI Microservice: Logistics Requirements Engine (LRE-Core).
Предоставляет REST API для КИС2 и веб-панели визуализатора.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from .schemas.request import TransportRequest
from .schemas.response import (
    RequirementInferenceResponse, GraphTrace, FeedbackPayload
)
from .engine.pipeline import InferencePipeline
from .engine.registry import (
    INPUT_SIGNALS, CONCEPT_KEYS, CONCEPTS_REGISTRY,
    REQUIREMENT_KEYS, REQUIREMENTS_REGISTRY
)
from .storage.trace_store import trace_store
from .config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Микросервис автоматического формирования требований к перевозке грузов на базе гибридной нейро-символьной архитектуры."
)

# Разрешаем CORS для автономного дашборда мониторинга
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = InferencePipeline()

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.post(
    "/v1/requirements/infer",
    response_model=RequirementInferenceResponse,
    status_code=status.HTTP_200_OK,
    tags=["Requirements Inference"]
)
def infer_requirements(request: TransportRequest):
    """
    Основной метод API для КИС2.
    Принимает параметры перевозки и возвращает перечень требований с обоснованиями и параметрами.
    """
    try:
        response, trace = pipeline.run(request)
        # Сохраняем трассировку для визуализатора
        trace_store.save_trace(trace)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка логического вывода: {str(e)}"
        )

@app.get(
    "/v1/traces/{trace_id}",
    response_model=GraphTrace,
    status_code=status.HTTP_200_OK,
    tags=["Visualizer & Monitoring"]
)
def get_trace(trace_id: str):
    """
    Получить граф трассировки по ID для визуализации активации нейронов.
    """
    trace = trace_store.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Трассировка {trace_id} не найдена"
        )
    return trace

@app.get(
    "/v1/traces/latest/active",
    response_model=GraphTrace,
    status_code=status.HTTP_200_OK,
    tags=["Visualizer & Monitoring"]
)
def get_latest_trace():
    """
    Получить последнюю трассировку инференса для отображения на дашборде мониторинга.
    """
    trace = trace_store.get_latest_trace()
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В истории еще нет выполненных трассировок"
        )
    return trace

@app.get(
    "/v1/traces",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    tags=["Visualizer & Monitoring"]
)
def list_traces(limit: int = 20):
    """
    Список последних выполненных расчетов.
    """
    return trace_store.list_traces(limit=limit)

@app.get(
    "/v1/graph-schema",
    status_code=status.HTTP_200_OK,
    tags=["Visualizer & Monitoring"]
)
def get_graph_schema():
    """
    Возвращает метаданные схемы слоев нейросети (узлы X, Z, Y) для визуализатора.
    """
    inputs = [
        {"id": inp, "label": inp.replace("x_", ""), "type": "input"}
        for inp in INPUT_SIGNALS
    ]
    concepts = [
        {
            "id": c_key,
            "label": CONCEPTS_REGISTRY[c_key]["name"],
            "description": CONCEPTS_REGISTRY[c_key]["description"],
            "type": "concept"
        }
        for c_key in CONCEPT_KEYS
    ]
    requirements = [
        {
            "id": r_key,
            "label": f"{r_key} {REQUIREMENTS_REGISTRY[r_key]['name']}",
            "area": REQUIREMENTS_REGISTRY[r_key]["area"],
            "type": "requirement"
        }
        for r_key in REQUIREMENT_KEYS
    ]
    return {
        "inputs": inputs,
        "concepts": concepts,
        "requirements": requirements
    }

@app.post(
    "/v1/feedback",
    status_code=status.HTTP_200_OK,
    tags=["Feedback & Continuous Learning"]
)
def record_feedback(payload: FeedbackPayload):
    """
    Прием обратной связи от логиста в КИС2 (принято/отклонено) для будущего дообучения.
    """
    trace_store.save_feedback(payload)
    return {"status": "FEEDBACK_RECORDED", "trace_id": payload.trace_id}
