"""
Детерминированный Rule Engine: нормативные, физические и регуляторные правила.
Формирует:
1. Hard rules mask (жесткие смещения для гарантированного включения требований);
2. Rationale (обоснования с ссылками на нормативы);
3. Промежуточные факты.
"""
from typing import Dict, List, Tuple, Any
from ..schemas.request import TransportRequest
from .registry import REQUIREMENT_KEYS, REQUIREMENT_INDEX

class RuleCheckResult:
    def __init__(self):
        # Маска смещений для выходных требований [len(REQUIREMENT_KEYS)]
        self.hard_rule_mask: Dict[str, float] = {k: 0.0 for k in REQUIREMENT_KEYS}
        # Обоснования срабатывания жестких правил
        self.rationales: Dict[str, str] = {}
        # Промежуточные физические факты
        self.flags: Dict[str, bool] = {}

class RuleEngine:
    # Нормативы ПДД РФ и ЕАЭС
    STANDARD_MAX_WIDTH = 2.55       # м (стандартный изотерм/тент)
    REF_MAX_WIDTH = 2.60            # м (рефрижератор)
    STANDARD_MAX_TOTAL_HEIGHT = 4.0 # м (предельная высота автопоезда с грузом)
    STANDARD_TRAILER_HEIGHT = 1.30  # м (высота стандартного тента)
    LOWBOY_TRAILER_HEIGHT = 0.85    # м (высота низкорамного трала)
    STANDARD_MAX_LENGTH = 13.6      # м (стандартная длина еврофуры)
    HEAVY_PIECE_THRESHOLD_KG = 1500 # кг (1.5 т - граница тяжелого неделимого места)
    HEAVY_WEIGHT_CRITICAL_KG = 20000# кг (20 т - граница тяжеловесности)

    def evaluate(self, request: TransportRequest) -> RuleCheckResult:
        res = RuleCheckResult()
        cargo = request.cargo
        dims = cargo.dimensions
        
        # 1. Проверка негабарита по ширине
        is_oversize_width = dims.width_m > self.STANDARD_MAX_WIDTH
        res.flags["is_oversize_width"] = is_oversize_width
        if is_oversize_width:
            res.hard_rule_mask["TR-03"] = 1.0  # Спецтранспорт
            res.hard_rule_mask["MR-03"] = 1.0  # Спецразрешение
            res.rationales["TR-03"] = (
                f"Ширина груза {dims.width_m:.2f} м превышает нормативный габарит "
                f"({self.STANDARD_MAX_WIDTH} м). Требуется специализированный транспорт с уширителями."
            )
            res.rationales["MR-03"] = (
                f"Ширина {dims.width_m:.2f} м является негабаритной. "
                "Требуется специальное разрешение на движение КТГ по автодорогам."
            )

        # 2. Проверка негабарита по высоте
        # Если погрузить на стандартный тент (1.30м), какая будет общая высота?
        total_height_standard = dims.height_m + self.STANDARD_TRAILER_HEIGHT
        total_height_lowboy = dims.height_m + self.LOWBOY_TRAILER_HEIGHT
        
        is_high_cargo = dims.height_m > 2.70
        is_oversize_height = total_height_lowboy > self.STANDARD_MAX_TOTAL_HEIGHT
        res.flags["is_high_cargo"] = is_high_cargo
        res.flags["is_oversize_height"] = is_oversize_height
        
        if is_high_cargo:
            res.hard_rule_mask["TR-03"] = 1.0
            if "TR-03" not in res.rationales:
                res.rationales["TR-03"] = (
                    f"Высота груза {dims.height_m:.2f} м не позволяет перевозку в стандартном полуприцепе. "
                    "Требуется низкорамный трал (погрузочная высота ≤ 0.85 м)."
                )
        if is_oversize_height:
            res.hard_rule_mask["MR-03"] = 1.0
            res.rationales["MR-03"] = (
                f"Общая высота автопоезда с грузом ({total_height_lowboy:.2f} м) "
                f"превышает допустимые {self.STANDARD_MAX_TOTAL_HEIGHT} м. Требуется спецразрешение и согласование мостов/ЛЭП."
            )

        # 3. Проверка негабарита по длине
        is_oversize_length = dims.length_m > self.STANDARD_MAX_LENGTH
        res.flags["is_oversize_length"] = is_oversize_length
        if is_oversize_length:
            res.hard_rule_mask["TR-03"] = 1.0
            res.hard_rule_mask["MR-03"] = 1.0
            res.rationales["TR-03"] = (
                f"Длина груза {dims.length_m:.2f} м превышает полезную длину стандартного полуприцепа (13.6 м). "
                "Требуется телескопический / раздвижной трал."
            )
            res.rationales["MR-03"] = (
                f"Длина автопоезда превысит норматив 20.0 м. Требуется спецразрешение на негабаритную длину."
            )

        # 4. Проверка веса неделимого места (> 1.5 т)
        is_heavy_single_piece = (
            dims.heavy_single_place is True or 
            dims.weight_kg >= self.HEAVY_PIECE_THRESHOLD_KG
        )
        res.flags["is_heavy_single_piece"] = is_heavy_single_piece
        if is_heavy_single_piece:
            res.hard_rule_mask["KR-01"] = 1.0  # Спецкрепление
            res.hard_rule_mask["PG-03"] = 1.0  # Погрузочное оборудование / кран
            res.rationales["KR-01"] = (
                f"Вес грузоместа {dims.weight_kg / 1000:.2f} т (≥ 1.5 т) требует обязательного специального крепления "
                "(цепные стяжки, талрепы, противоскользящие маты) согласно правилам безопасного размещения грузов."
            )
            res.rationales["PG-03"] = (
                f"Вес места {dims.weight_kg / 1000:.2f} т исключает ручные ПРР. "
                "Требуется сертифицированное крановое оборудование или тяжелый вилочный погрузчик."
            )

        # 5. Тяжеловесность критическая (> 20 т на одно место)
        is_critical_heavy = dims.weight_kg >= self.HEAVY_WEIGHT_CRITICAL_KG
        res.flags["is_critical_heavy"] = is_critical_heavy
        if is_critical_heavy:
            res.hard_rule_mask["TR-03"] = 1.0
            res.hard_rule_mask["MR-03"] = 1.0
            res.hard_rule_mask["DC-03"] = 1.0  # Данные о центре тяжести
            res.rationales["DC-03"] = (
                f"Масса места {dims.weight_kg / 1000:.2f} т требует обязательного предоставления чертежей завода с точными координатами центра тяжести."
            )

        # 6. Опасные грузы (IMO / UN)
        has_danger = bool(cargo.danger.imo or cargo.danger.un)
        res.flags["has_danger"] = has_danger
        if has_danger:
            res.hard_rule_mask["TR-02"] = 1.0  # Выбор типа ТС (ADR)
            res.hard_rule_mask["DC-06"] = 1.0  # Разрешительные документы (паспорт безопасности MSDS, свидетельство ADR)
            res.rationales["TR-02"] = (
                f"Груз опасный (UN: {cargo.danger.un or 'не указан'}, IMO: {cargo.danger.imo or 'ADR'}). "
                "Требуется транспортное средство, допущенное к перевозке опасных грузов (свидетельство ДОПОГ/ADR)."
            )
            res.rationales["DC-06"] = (
                "Для опасного груза требуются паспорт безопасности химической продукции (MSDS) и аварийная карточка."
            )

        # 7. Контроли ВЕТ / СКК / КФК
        has_control = cargo.danger.vet or cargo.danger.kfk or cargo.danger.skk
        res.flags["has_control"] = has_control
        if has_control:
            res.hard_rule_mask["DC-05"] = 1.0  # Сертификаты
            res.hard_rule_mask["MR-05"] = 1.0  # Пограничный переход
            res.hard_rule_mask["TM-02"] = 1.0  # СВХ
            res.rationales["DC-05"] = (
                "Груз подлежит специальному нетарифному контролю (ВЕТ/СКК/КФК). "
                "Требуется предоставление ветеринарных/фитосанитарных сертификатов."
            )
            res.rationales["MR-05"] = (
                "Пересечение границы допускается только через специализированные пункты пропуска, "
                "оборудованные постами фитосанитарного/ветеринарного контроля."
            )
            res.rationales["TM-02"] = (
                "Таможенное оформление возможно только на СВХ, включенном в реестр для подконтрольных товаров."
            )

        # 8. Условия поставки Incoterms
        incoterms = (request.incoterms or "").upper()
        if incoterms in ["EXW", "FCA"]:
            res.hard_rule_mask["DC-07"] = 1.0  # Экспортные документы
            res.rationales["DC-07"] = (
                f"Условия поставки {incoterms}: организация экспортного таможенного оформления "
                "и подготовка экспортной декларации (EX-1) возлагается на сторону экспедитора/покупателя."
            )

        return res
