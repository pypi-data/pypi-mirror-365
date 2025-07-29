
# marmel-grammar

Библиотека русской морфологии и транслитерации для Python

## Описание

`marmel-grammar` — это мощная библиотека для работы с русскими именами, включающая транслитерацию, определение рода, склонение по падежам и спряжение глаголов. Библиотека поддерживает автоматическое склонение имен, не входящих в базу данных, и работу с кастомными именами.

## Установка

```bash
pip install marmel-grammar
```

## Быстрый старт

```python
from marmel_grammar import MarmelGrammar

# Создание экземпляра библиотеки
grammar = MarmelGrammar()

# Транслитерация имени
russian_name = grammar.transliterate_to_russian("Mika")
print(russian_name)  # Мика

# Определение рода
gender = grammar.detect_gender(russian_name)
print(gender)  # female

# Склонение по падежам
print(grammar.decline(russian_name, "gen"))  # Мики
```

## Основные возможности

### 1. Транслитерация имен

Библиотека поддерживает транслитерацию с английского на русский язык с использованием интеллектуальных правил и базы специальных имен.

```python
grammar = MarmelGrammar()

# Базовая транслитерация
print(grammar.transliterate_to_russian("Alexander"))  # Александр
print(grammar.transliterate_to_russian("Maria"))      # Мария
print(grammar.transliterate_to_russian("Mika"))       # Мика

# Специальные имена из базы данных
print(grammar.transliterate_to_russian("anna"))       # Анна
print(grammar.transliterate_to_russian("john"))       # Джон
print(grammar.transliterate_to_russian("gazenvagen")) # Газенваген

# Пакетная транслитерация
names = ["Alexander", "Maria", "John", "Mika"]
result = grammar.batch_transliterate(names)
print(result)
# {'Alexander': 'Александр', 'Maria': 'Мария', 'John': 'Джон', 'Mika': 'Мика'}
```

### 2. Определение рода

Автоматическое определение рода имени на основе базы данных и морфологических правил.

```python
grammar = MarmelGrammar()

# Имена из базы данных
print(grammar.detect_gender("Мария"))    # female
print(grammar.detect_gender("Иван"))     # male
print(grammar.detect_gender("Саша"))     # unisex

# Автоматическое определение по окончаниям
print(grammar.detect_gender("Алина"))    # female (окончание -а)
print(grammar.detect_gender("Михаил"))   # male (согласная)
print(grammar.detect_gender("Олег"))     # male (согласная)
```

### 3. Склонение имен по падежам

Полная поддержка русских падежей с автоматическим склонением неизвестных имен.

```python
grammar = MarmelGrammar()

# Склонение конкретного имени
name = "Мария"
print(grammar.decline(name, "nom"))   # Мария (именительный)
print(grammar.decline(name, "gen"))   # Марии (родительный)
print(grammar.decline(name, "dat"))   # Марии (дательный)
print(grammar.decline(name, "acc"))   # Марию (винительный)
print(grammar.decline(name, "prep"))  # Марии (предложный)

# Получение всех форм сразу
all_forms = grammar.get_all_forms("Ника")
print(all_forms)
# {'nom': 'Ника', 'gen': 'Ники', 'dat': 'Нике', 'acc': 'Нику', 'prep': 'Нике'}

# Автоматическое склонение неизвестных имен
all_forms = grammar.get_all_forms("Мика")
print(all_forms)
# {'nom': 'Мика', 'gen': 'Мики', 'dat': 'Мике', 'acc': 'Мику', 'prep': 'Мике'}
```

### 4. Спряжение глаголов

Спряжение глаголов по временам и лицам с поддержкой рода подлежащего.

```python
grammar = MarmelGrammar()

# Простое спряжение в прошедшем времени
print(grammar.conjugate("танцевать", "past", "Мария"))  # танцевала
print(grammar.conjugate("танцевать", "past", "Иван"))   # танцевал
print(grammar.conjugate("пукнуть", "past", "Ноах"))     # пукнул

# Спряжение в настоящем времени
print(grammar.conjugate("танцевать", "present", "я"))   # танцую
print(grammar.conjugate("танцевать", "present", "ты"))  # танцуешь
print(grammar.conjugate("танцевать", "present", "он"))  # танцует

# Умное спряжение (для глаголов не в базе)
print(grammar.smart_conjugate("работать", "Мария"))     # работала
print(grammar.conjugate_any_verb("изучать", "Иван"))    # изучал
```

### 5. Создание предложений

Автоматическое создание грамматически правильных предложений.

```python
grammar = MarmelGrammar()

# Обычные предложения (субъект + глагол + объект в винительном падеже)
sentence = grammar.make_sentence("Иван", "читать", "Анна")
print(sentence)  # Иван читал Анну.

sentence = grammar.make_sentence("Мария", "изучать", "Python")
print(sentence)  # Мария изучала Python.

# Предложения с предлогом "для" (объект в родительном падеже) (marmel-grammar — не умеет подставлять предлоги, мы совершенствуемся)
sentence = grammar.make_sentence_for("Ноах", "пукнуть", "Мика")
print(sentence)  # Ноах пукнул для Мики.

sentence = grammar.make_sentence_for("Александр", "работать", "Мария")
print(sentence)  # Александр работал для Марии.
```

### 6. Обработка кастомных имен

Библиотека корректно обрабатывает имена с нестандартными символами.

```python
grammar = MarmelGrammar()

# Имена с нестандартными символами остаются без изменений
custom_name = "ᴇɢʟᴀɴᴛɪɴᴀ"
processed = grammar.clean_name(custom_name)
print(processed)  # ᴇɢʟᴀɴᴛɪɴᴀ

# Обычная очистка сохраняет пробелы только в начале/конце
name_with_spaces = "  Мария Ивановна  "
cleaned = grammar.clean_name(name_with_spaces)
print(f"'{cleaned}'")  # 'Мария ивановна'
```

### 7. Добавление новых имен

Расширение базы данных собственными именами.

```python
grammar = MarmelGrammar()

# Добавление нового имени с полными падежными формами
new_name_cases = {
    "nom": "Артур",
    "gen": "Артура", 
    "dat": "Артуру",
    "acc": "Артура",
    "prep": "Артуре"
}

grammar.add_name("Артур", "male", new_name_cases)

# Теперь можно использовать новое имя
print(grammar.decline("Артур", "gen"))  # Артура
print(grammar.detect_gender("Артур"))   # male
```

## Справочник методов

### Основные методы

| Метод | Описание | Параметры | Возвращает |
|-------|----------|-----------|------------|
| `transliterate_to_russian(text)` | Транслитерация с английского на русский | `text: str` | `str` |
| `detect_gender(name)` | Определение рода имени | `name: str` | `str` ('male'/'female'/'unisex') |
| `decline(name, case, gender=None)` | Склонение имени по падежу | `name: str, case: str, gender: str` | `str` |
| `get_all_forms(name)` | Получение всех падежных форм | `name: str` | `Dict[str, str]` |
| `conjugate(verb, tense, subject)` | Спряжение глагола | `verb: str, tense: str, subject: str` | `str` |
| `make_sentence(subj, verb, obj, tense='past')` | Создание предложения | `subj: str, verb: str, obj: str, tense: str` | `str` |
| `make_sentence_for(subj, verb, obj, tense='past')` | Предложение с "для" | `subj: str, verb: str, obj: str, tense: str` | `str` |
| `clean_name(name)` | Очистка имени | `name: str` | `str` |
| `add_name(name, gender, cases)` | Добавление нового имени | `name: str, gender: str, cases: Dict` | `None` |

### Дополнительные методы

| Метод | Описание | Параметры | Возвращает |
|-------|----------|-----------|------------|
| `batch_transliterate(names)` | Пакетная транслитерация | `names: List[str]` | `Dict[str, str]` |
| `smart_conjugate(verb, subject, tense='past')` | Умное спряжение | `verb: str, subject: str, tense: str` | `str` |
| `conjugate_any_verb(verb, subject, tense='past')` | Спряжение любого глагола | `verb: str, subject: str, tense: str` | `str` |

## Поддерживаемые падежи

| Падеж | Код | Вопросы | Пример |
|-------|-----|---------|--------|
| Именительный | `nom` | кто? что? | Мария |
| Родительный | `gen` | кого? чего? | Марии |
| Дательный | `dat` | кому? чему? | Марии |
| Винительный | `acc` | кого? что? | Марию |
| Предложный | `prep` | о ком? о чем? | Марии |

## Поддерживаемые роды

| Род | Код | Описание | Примеры |
|-----|-----|----------|---------|
| Мужской | `male` | Мужские имена | Иван, Александр, Игорь |
| Женский | `female` | Женские имена | Мария, Анна, Ольга |
| Универсальный | `unisex` | Имена любого рода | Саша, Женя, Валя |

## Поддерживаемые времена глаголов

| Время | Код | Описание | Пример |
|-------|-----|----------|--------|
| Прошедшее | `past` | Действие в прошлом | танцевал, читала |
| Настоящее | `present` | Действие в настоящем | танцую, читает |

## Полный пример использования

```python
from marmel_grammar import MarmelGrammar

def demo():
    # Создаем экземпляр библиотеки
    grammar = MarmelGrammar()
    
    # Тест транслитерации
    print("=== Транслитерация ===")
    english_names = ["Mika", "Alexander", "Anna", "John"]
    for name in english_names:
        russian_name = grammar.transliterate_to_russian(name)
        print(f"{name} → {russian_name}")
    
    # Тест определения рода и склонения
    print("\n=== Склонение имен ===")
    test_names = ["Мика", "Александр", "Анна"]
    
    for name in test_names:
        gender = grammar.detect_gender(name)
        print(f"\nИмя: {name} (род: {gender})")
        
        forms = grammar.get_all_forms(name)
        for case, form in forms.items():
            print(f"  {case}: {form}")
    
    # Тест спряжения глаголов
    print("\n=== Спряжение глаголов ===")
    verbs = ["танцевать", "читать", "работать"]
    subjects = ["Мария", "Иван", "Саша"]
    
    for verb in verbs:
        for subject in subjects:
            conjugated = grammar.conjugate(verb, "past", subject)
            print(f"{subject} {conjugated}")
    
    # Тест создания предложений
    print("\n=== Создание предложений ===")
    sentences = [
        ("Иван", "читать", "Анна"),
        ("Мария", "изучать", "Python"),
        ("Саша", "готовить", "обед")
    ]
    
    for subj, verb, obj in sentences:
        sentence1 = grammar.make_sentence(subj, verb, obj)
        sentence2 = grammar.make_sentence_for(subj, verb, obj)
        print(f"Обычное: {sentence1}")
        print(f"С 'для': {sentence2}")
        print()

if __name__ == "__main__":
    demo()
```

## База данных

Библиотека включает мелкую базу данных + автоматически обрабатывает:

- **Имена**: более 50 популярных русских имен с полными падежными формами
- **Глаголы**: 20+ глаголов с формами прошедшего и настоящего времени
- **Специальные имена**: англо-русские соответствия для популярных имен
- **Транслитерация**: полная карта транслитерации английских букв и сочетаний

## Особенности

### Автоматическое склонение
Для имен, отсутствующих в базе данных, библиотека применяет морфологические правила русского языка.

### Обработка кастомных имен
Имена с нестандартными символами (например, стилизованными Unicode-символами) сохраняются без изменений.

### Умное спряжение
Глаголы автоматически спрягаются даже если отсутствуют в базе данных, используя стандартные правила русского языка.

### Сохранение пробелов
При очистке имен пробелы удаляются только в начале и в конце строки, сохраняя внутренние пробелы для составных имен.

## Версия и автор

**Версия**: 0.1.8b3

**Автор**: Dev-Marmel  
**Email**: marmelgpt@gmail.com  
**Telegram**: [@dev_marmel](https://t.me/dev_marmel)

## Changelog

### 0.1.8b3
- Исправлена проблема со склонением в винительном/родительном падеже
- Удалена функция обратной транслитерации
- Улучшена обработка кастомных имен
- Обновлены правила очистки имен
- Расширена база данных глаголов
