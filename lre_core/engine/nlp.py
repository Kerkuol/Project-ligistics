"""
Легковесный семантический анализатор текста примечаний и наименования груза.
Работает локально, детерминированно и быстро (<1 мс), без внешних тяжелых моделей.
"""
import re
from typing import Dict, Any
from ..schemas.request import TransportRequest

class SemanticTextParser:
    # Семантические паттерны логистических условий
    PATTERNS = {
        "no_tilt": [
            r"не\s+кантовать",
            r"запрет(щено)?\s+кантован",
            r"не\s+переворачивать",
            r"хрупк(ий|ое|ая|ость)",
            r"стекл(о|янн)",
            r"прецизионн",
            r"электроник",
            r"деликатн",
            r"вертикальн(о|ое)\s+положен"
        ],
        "crane_top": [
            r"кран[\s\-]?балк",
            r"мостов(ой|ым)\s+кран",
            r"автокран",
            r"только\s+кран",
            r"верхн(яя|ей)\s+погрузк",
            r"погрузка\s+через\s+верх",
            r"растентовк(а|у)\s+крыш",
            r"траверс",
            r"строповк",
            r"спецзахват"
        ],
        "moisture_protect": [
            r"боит(ся)?\s+влаг",
            r"влаго(защит|стойк)",
            r"сух(ой|ом)\s+(трюм|склад|кузов)",
            r"гидроизоляц",
            r"вакуумн(ая|ой)\s+упаковк",
            r"термоусад(очн|ка)",
            r"тент\s+обязател",
            r"корроз",
            r"конденсат"
        ],
        "direct_only": [
            r"без\s+перегруз",
            r"без\s+перевалк",
            r"перетарк(а|у)\s+запрещ",
            r"прям(ой|ым)\s+(транспорт|рейс|авто|машин)",
            r"не\s+перегружать",
            r"не\s+перецеплять"
        ],
        "urgent_delivery": [
            r"срочн",
            r"экспресс",
            r"горящ",
            r"штраф\s+за\s+просрочк",
            r"жестк(ий|ие)\s+срок"
        ]
    }

    def __init__(self):
        # Компилируем регулярные выражения для максимального быстродействия
        self._compiled = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.PATTERNS.items()
        }

    def parse(self, request: TransportRequest) -> Dict[str, float]:
        """
        Анализирует все текстовые поля и возвращает нормализованные сигналы [0.0..1.0].
        """
        # Объединяем весь релевантный текст заявки
        text_corpus = " ".join(filter(None, [
            request.cargo.name,
            request.cargo.dimensions.package_type,
            request.notes.request_notes,
            request.notes.loading_notes,
            request.notes.delivery_notes,
            request.origin.notes,
            request.destination.notes
        ]))

        signals = {}
        for category, regexes in self._compiled.items():
            matched = False
            for r in regexes:
                if r.search(text_corpus):
                    matched = True
                    break
            signals[category] = 1.0 if matched else 0.0

        return signals
