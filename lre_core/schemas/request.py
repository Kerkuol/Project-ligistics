from typing import Optional, List
from pydantic import BaseModel, Field

class Location(BaseModel):
    country: Optional[str] = Field(None, description="Страна")
    city: Optional[str] = Field(None, description="Город")
    address: Optional[str] = Field(None, description="Точный адрес")
    contact_info: Optional[str] = Field(None, description="Контактные данные")
    legal_address: Optional[str] = Field(None, description="Юридический адрес")
    notes: Optional[str] = Field(None, description="Примечания к локации")

class CargoDanger(BaseModel):
    imo: Optional[str] = Field(None, description="Класс IMO")
    un: Optional[str] = Field(None, description="UN номер опасного груза")
    vet: bool = Field(False, description="Ветеринарный контроль (ВЕТ)")
    skk: bool = Field(False, description="Санитарно-карантинный контроль (СКК)")
    kfk: bool = Field(False, description="Карантинный фитосанитарный контроль (КФК)")
    rf: bool = Field(False, description="Радиационный контроль (РФ)")

class CargoDimensions(BaseModel):
    length_m: float = Field(..., ge=0.0, description="Длина грузоместа (м)")
    width_m: float = Field(..., ge=0.0, description="Ширина грузоместа (м)")
    height_m: float = Field(..., ge=0.0, description="Высота грузоместа (м)")
    volume_m3: Optional[float] = Field(None, ge=0.0, description="Объём единицы (м3)")
    weight_kg: float = Field(..., ge=0.0, description="Вес единицы (кг)")
    package_type: Optional[str] = Field(None, description="Вид грузоместа (ящик, поддон, бочка, без упаковки и т.д.)")
    places_count: int = Field(1, ge=1, description="Количество мест")
    total_volume_m3: Optional[float] = Field(None, ge=0.0, description="Общий объём (м3)")
    total_weight_kg: Optional[float] = Field(None, ge=0.0, description="Общий вес (кг)")
    stackable: bool = Field(False, description="Возможность штабелирования (да/нет)")
    heavy_single_place: Optional[bool] = Field(None, description="Вес г/м > 1.5 т")

class CargoCost(BaseModel):
    value: Optional[float] = Field(None, ge=0.0, description="Стоимость груза")
    currency: Optional[str] = Field("USD", description="Валюта стоимости")

class CargoInfo(BaseModel):
    name: str = Field(..., description="Наименование груза")
    hs_code: Optional[str] = Field(None, description="Код ТН ВЭД (10 знаков или группа)")
    danger: CargoDanger = Field(default_factory=CargoDanger)
    dimensions: CargoDimensions
    cost: Optional[CargoCost] = Field(default_factory=CargoCost)

class InsuranceInfo(BaseModel):
    required: bool = Field(False, description="Требуется страхование")
    insured_sum: Optional[float] = Field(None, description="Страховая сумма")
    responsible_party: Optional[str] = Field(None, description="Сторона страхования (клиент/экспедитор)")

class NotesInfo(BaseModel):
    request_notes: Optional[str] = Field(None, description="Примечание к запросу в целом")
    loading_notes: Optional[str] = Field(None, description="Примечания по погрузке")
    delivery_notes: Optional[str] = Field(None, description="Примечания по доставке")

class TransportRequest(BaseModel):
    """
    Полная структура входных данных из КИС2:
    39 структурированных параметров + геоданные + примечания.
    """
    # 1. Метаданные запроса КИС2
    request_id: Optional[str] = Field(None, description="Номер / ID запроса в КИС2")
    initiator: Optional[str] = Field(None, description="Инициатор запроса / менеджер")
    created_at: Optional[str] = Field(None, description="Дата создания")
    client: Optional[str] = Field(None, description="Клиент / заказчик")
    supplier: Optional[str] = Field(None, description="Поставщик / грузоотправитель")
    services: Optional[List[str]] = Field(default_factory=list, description="Заказанные услуги")
    ready_date: Optional[str] = Field(None, description="Дата готовности груза")
    proforma_number: Optional[str] = Field(None, description="Номер проформы")
    
    # 2. Логистический базис и транспорт
    incoterms: Optional[str] = Field("FCA", description="Условия поставки (EXW, FCA, CPT, CIP, FOB, CIF, DAP, DDP)")
    primary_transport: Optional[str] = Field("автомобильный", description="Основной вид транспорта (авто, море, ж/д, авиа, мультимодал)")
    transport_units: Optional[str] = Field(None, description="Транспортные единицы")
    
    # 3. Маршрут
    origin: Location = Field(..., description="Место отправления / загрузки")
    destination: Location = Field(..., description="Место назначения / доставки")
    
    # 4. Данные о грузе (габариты, вес, коды, опасность)
    cargo: CargoInfo
    
    # 5. Страхование
    insurance: Optional[InsuranceInfo] = Field(default_factory=InsuranceInfo)
    
    # 6. Неструктурированные текстовые примечания
    notes: NotesInfo = Field(default_factory=NotesInfo)
