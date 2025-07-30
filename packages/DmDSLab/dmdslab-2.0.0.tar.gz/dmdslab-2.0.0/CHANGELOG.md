# История изменений

Все значимые изменения в DmDSLab документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект придерживается [Семантического версионирования](https://semver.org/lang/ru/).

## [2.0.0] - 2025-07-28

### 🎉 Главное в релизе

Версия 2.0 представляет полноценную интеграцию с UCI Machine Learning Repository! Теперь вы можете загружать датасеты прямо из UCI с автоматическим кешированием, определением типов задач и удобным API.

### ⚠️ BREAKING CHANGES

- **Минимальная версия Python теперь 3.11** (удалена поддержка 3.8, 3.9, 3.10)
- Переработан API для UCI Dataset Loader


### ✨ Новые возможности

- **UCI Dataset Loader** - Полноценный модуль для работы с UCI ML Repository
  - Загрузка датасетов по ID: `manager.load_dataset(53)`
  - Загрузка по имени: `load_uci_by_name('iris')`
  - Пакетная загрузка: `manager.load_datasets([53, 17, 19])`
  - Автоматическая интеграция с `ModelData`

- **Интеллектуальное кеширование**
  - Pickle-based кеш для быстрого доступа к загруженным данным
  - Автоматическое управление размером кеша
  - Принудительная перезагрузка: `force_reload=True`
  - Валидация целостности кеша с восстановлением

- **Автоматическое определение характеристик**
  - Определение типа задачи (классификация/регрессия/кластеризация)
  - Выявление категориальных признаков
  - Расчет статистики по датасетам
  - Обнаружение пропущенных значений

- **Progress Bars и логирование**
  - Визуализация процесса загрузки через tqdm
  - Настраиваемые уровни логирования (DEBUG, INFO, WARNING, ERROR)
  - Детальные отчеты о загрузке

- **Управление кешем**
  - `clear_cache()` - очистка всего кеша или отдельных датасетов
  - `get_cache_info()` - статистика использования кеша
  - Экспорт/импорт кеша для переноса между системами

### 🔧 Технические улучшения

- **Модульная архитектура**
  - Разделение на логические компоненты: manager, cache, metadata, types, utils
  - Четкая иерархия исключений для обработки ошибок
  - Расширяемая система типов данных

- **Улучшенная обработка ошибок**
  - Специализированные исключения: `DatasetNotFoundError`, `CacheError`, `NetworkError`
  - Graceful degradation при отсутствии интернета
  - Подробные сообщения об ошибках с контекстом

### Примеры использования

```python
# Быстрая загрузка популярного датасета
from dmdslab.datasets import load_uci_by_name
iris = load_uci_by_name('iris')

# Использование менеджера для расширенных возможностей
from dmdslab.datasets.uci import UCIDatasetManager
manager = UCIDatasetManager()

# Загрузка с progress bar
data = manager.load_dataset(53, show_progress=True)

# Пакетная загрузка
datasets = manager.load_datasets([53, 17, 19, 45])

# Управление кешем
info = manager.get_cache_info()
manager.clear_cache(dataset_id=53)  # Очистить конкретный
manager.clear_cache()  # Очистить весь кеш
```

---

## [1.0.1] - 2025-07-25
Обновлен readme.md и версии зависимых библиотек.
[1.0.1]: https://github.com/Dmatryus/DmDSLab/releases/tag/v1.0.1

## [1.0.0] - 2025-07-24

### 🎉 Первый стабильный релиз

[Содержимое остается как было...]

---

[2.0.0]: https://github.com/Dmatryus/DmDSLab/releases/tag/v2.0.0
[1.0.1]: https://github.com/Dmatryus/DmDSLab/releases/tag/v1.0.1
[1.0.0]: https://github.com/Dmatryus/DmDSLab/releases/tag/v1.0.0