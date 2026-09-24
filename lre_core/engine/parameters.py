"""
Блок параметризации (Slot Filling) для активных требований.
Вычисляет конкретные физические, технические и юридические параметры
для каждого требования, превысившего порог активации.
"""
from typing import Dict, Any
from ..schemas.request import TransportRequest

class ParameterExtractor:
    def enrich(self, req_id: str, request: TransportRequest, probability: float) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        cargo = request.cargo
        dims = cargo.dimensions
        weight_tons = dims.weight_kg / 1000.0
        
        # 1. TR-02 / TR-03 / TR-04 (Транспорт)
        if req_id in ["TR-02", "TR-03", "TR-04"]:
            if dims.height_m > 3.0:
                vehicle_type = "Сверхнизкорамный трал (постель/корыто) с погрузочной высотой 0.35 - 0.50 м"
            elif dims.height_m > 2.6:
                vehicle_type = "Низкорамный полуприцеп (трал) с погрузочной высотой 0.85 - 0.90 м"
            elif dims.length_m > 13.6:
                vehicle_type = "Раздвижной (телескопический) полуприцеп"
            elif weight_tons > 35.0:
                vehicle_type = "Многоосный тяжеловесный модульный прицеп (Goldhofer/Scheuerle)"
            elif cargo.danger.imo or cargo.danger.un:
                vehicle_type = "Транспортное средство категории EX/II, EX/III, FL или AT (допуск ADR)"
            else:
                vehicle_type = "Специализированная открытая платформа / трал"
                
            features = []
            if dims.width_m > 2.55:
                features.append(f"Уширители платформы до {(dims.width_m + 0.2):.2f} м")
            if weight_tons > 15.0:
                features.append("Усиленные крепежные проушины (не менее 10 000 daN)")
            if dims.length_m > 13.6:
                features.append(f"Длина рабочей площадки в раздвинутом виде не менее {dims.length_m + 1.0:.1f} м")
                
            params = {
                "recommended_vehicle": vehicle_type,
                "required_features": features,
                "min_carrying_capacity_tons": round(weight_tons * 1.1, 1),
                "cargo_dimensions_actual": f"{dims.length_m:.2f} x {dims.width_m:.2f} x {dims.height_m:.2f} м"
            }

        # 2. TR-07 / TR-08 (Прямой транспорт / перегруз)
        elif req_id in ["TR-07", "TR-08"]:
            params = {
                "direct_route_mandatory": True,
                "allow_transshipment": False,
                "allow_truck_tractor_swap": True, # Перецепка тягача обычно допустима
                "condition": "Исключить перетарку/кантование груза на промежуточных складах и терминалах"
            }

        # 3. KR-01 / KR-02 / KR-03 (Крепление)
        elif req_id in ["KR-01", "KR-02", "KR-03"]:
            if weight_tons > 10.0:
                method = "Крепление цепными стяжками (талрепы / рэтчеты) по диагональной схеме + упорные брусья"
                lashing_capacity = 10000 # daN
                min_chains = max(4, int(weight_tons // 5) * 2)
            else:
                method = "Текстильные стяжные ремни (50 мм, 5000 daN) + противоскользящие резиновые маты"
                lashing_capacity = 5000
                min_chains = max(4, int(dims.places_count * 2))
                
            params = {
                "lashing_method": method,
                "min_lashing_capacity_daN": lashing_capacity,
                "recommended_points_count": min_chains,
                "anti_slip_mats_required": True,
                "compliance_standard": "EN 12195-1 / ГОСТ 26653-85"
            }

        # 4. PG-01 / PG-03 (Погрузка / Оборудование)
        elif req_id in ["PG-01", "PG-03"]:
            # Расчет требуемой грузоподъемности с коэффициентом запаса 25-30%
            crane_capacity = max(5.0, round(weight_tons * 1.3, 1))
            rigging = []
            if weight_tons > 15.0:
                rigging.append("Линейная или пространственная траверса для исключения сдавливания груза стропами")
            if dims.length_m > 6.0:
                rigging.append("Четырехветвевой цепной или текстильный строп (паук) с регулировкой длины ветвей")
            else:
                rigging.append("Круглопрядные текстильные стропы повышенной грузоподъемности")
                
            params = {
                "equipment_type": "Автомобильный или мостовой кран",
                "min_crane_capacity_tons": crane_capacity,
                "rigging_equipment": rigging,
                "loading_method": "Вертикальная погрузка через верх / открытую платформу"
            }

        # 5. MR-03 (Специальное разрешение)
        elif req_id == "MR-03":
            oversize_types = []
            if dims.width_m > 2.55:
                oversize_types.append(f"По ширине: {dims.width_m:.2f} м (> 2.55 м)")
            if dims.height_m + 0.85 > 4.0:
                oversize_types.append(f"По высоте в сцепе: {dims.height_m + 0.85:.2f} м (> 4.00 м)")
            if dims.length_m > 13.6:
                oversize_types.append(f"По длине автопоезда: > 20.0 м (груз {dims.length_m:.2f} м)")
            if weight_tons > 20.0:
                oversize_types.append(f"По общей массе/нагрузкам на оси: вес груза {weight_tons:.1f} т")
                
            params = {
                "permit_category": "Специальное разрешение на перевозку крупногабаритного / тяжеловесного груза (КТГ)",
                "exceeded_parameters": oversize_types,
                "pilot_cars_escort_required": (dims.width_m > 3.5 or dims.length_m > 24.0 or dims.height_m + 0.85 > 4.5),
                "route_approval": "Требуется согласование владельцев автодорог, мостовых переходов и контактных сетей"
            }

        # 6. DC-03 (Данные о центре тяжести)
        elif req_id == "DC-03":
            params = {
                "document_required": "Схема строповки и чертеж завода-изготовителя с указанием координат центра тяжести (CG)",
                "critical_reason": f"Большая масса ({weight_tons:.1f} т) и габаритная высота ({dims.height_m:.2f} м) создают риск опрокидывания при транспортировке"
            }

        # 7. DC-06 (Разрешительные документы / ADR)
        elif req_id == "DC-06":
            docs = []
            if cargo.danger.imo or cargo.danger.un:
                docs.extend(["Паспорт безопасности вещества (MSDS / ПБХП)", "Письменные инструкции по ДОПОГ", "Свидетельство ДОПОГ водителя"])
            if cargo.danger.vet or cargo.danger.kfk or cargo.danger.skk:
                docs.extend(["Ветеринарный / фитосанитарный сертификат страны происхождения", "Разрешение на ввоз/транзит"])
            params = {
                "required_documents": docs
            }

        # 8. ST-01 / ST-02 (Страхование)
        elif req_id in ["ST-01", "ST-02"]:
            cost_val = cargo.cost.value if cargo.cost and cargo.cost.value else 0.0
            curr = cargo.cost.currency if cargo.cost and cargo.cost.currency else "USD"
            params = {
                "insurance_type": "Страхование ответственности экспедитора / Спецстрахование груза 'С ответственностью за все риски' (All Risks)",
                "insured_amount_recommended": round(cost_val * 1.10, 2) if cost_val > 0 else "По инвойсной стоимости + 10%",
                "currency": curr
            }

        return params
