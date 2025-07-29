# marmel_grammar/grammar.py
import re
from typing import Dict, List, Union, Optional
from .dataset import *

class MarmelGrammar:

    def __init__(self):
        self._load_dataset()
        self._init_reverse_translit()

    def _load_dataset(self):
        self.NAMES = NAMES
        self.VERBS = VERBS
        self.SPECIAL_NAMES = SPECIAL_NAMES
        self.TRANSLIT_MAP = TRANSLIT_MAP

    def _init_reverse_translit(self):
        self.REVERSE_TRANSLIT_MAP = {v: k for k, v in self.TRANSLIT_MAP.items()}

    def clean_name(self, name: str) -> str:
        if not name:
            return ''
        cleaned = re.sub(r'[^а-яА-ЯёЁa-zA-Z]', '', name)
        cleaned = cleaned.strip().capitalize()
        return cleaned

    def detect_gender(self, name: str) -> str:
        name = self.clean_name(name)

        for gender in self.NAMES:
            if name in self.NAMES[gender]:
                return gender

        if name.endswith(('а', 'я', 'ия')):
            return 'female'
        if name.endswith('ь'):
            return 'male'
        return 'male'

    def decline(self, name: str, case: str, gender: str = None) -> str:
        name = self.clean_name(name)
        gender = gender or self.detect_gender(name)

        if gender in self.NAMES and name in self.NAMES[gender] and case in self.NAMES[gender][name]:
            return self.NAMES[gender][name][case]

        if case == 'nom':
            return name
        elif case == 'gen':
            if gender == 'female' or (gender == 'unisex' and name.endswith(('а', 'я'))):
                if name.endswith('а'):
                    return name[:-1] + 'ы'
                elif name.endswith('я'):
                    return name[:-1] + 'и'
                return name[:-1] + 'и'
            return name + 'а'
        elif case == 'dat':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'у'
            else:
                if name.endswith(('а', 'я')):
                    return name[:-1] + 'е'
                return name + 'е'
        elif case == 'acc':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'а'
            else:
                if name.endswith('а'):
                    return name[:-1] + 'у'
                return name[:-1] + 'ю'
        elif case == 'prep':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'е'
            else:
                if name.endswith(('а', 'я')):
                    return name[:-1] + 'е'
                return name + 'е'

        return name

    def conjugate(self, verb: str, tense: str, subject: str) -> str:
        if verb in self.VERBS and tense in self.VERBS[verb]:
            forms = self.VERBS[verb][tense]

            if tense == 'past':
                if subject.lower() in ('они', 'вы', 'мы'):
                    return forms['они']
                gender = self.detect_gender(subject)
                if gender == 'male':
                    return forms['он']
                elif gender == 'female':
                    return forms['она']
                elif gender == 'unisex':
                    return forms['он']
                else:
                    return forms['оно']

            elif tense == 'present':
                subject_lower = subject.lower()
                if subject_lower in forms:
                    return forms[subject_lower]
                else:
                    return forms.get('он', verb)

        return verb

    def smart_conjugate(self, verb: str, subject: str, tense: str = 'past') -> str:
        base_verb = verb.lower()

        if base_verb in self.VERBS:
            return self.conjugate(base_verb, tense, subject)

        if base_verb.endswith('ть'):
            stem = base_verb[:-2]
            gender = self.detect_gender(subject)

            if tense == 'past':
                if gender == 'female':
                    return stem + 'ла'
                elif gender == 'male':
                    return stem + 'л'
                else:
                    return stem + 'ло'
            elif tense == 'present':
                return stem + 'ет'

        return verb

    def asc(self, name: str, verb: str, tense: str = 'past') -> str:
        declined_name = self.decline(name, 'nom')
        conjugated_verb = self.smart_conjugate(verb, name, tense)
        return f'{declined_name} {conjugated_verb}'

    def make_sentence(self, subj: str, verb: str, obj: str, tense: str = 'past') -> str:
        declined_subj = self.decline(subj, 'nom')
        conjugated_verb = self.conjugate(verb, tense, subj)
        declined_obj = self.decline(obj, 'acc')

        return f'{declined_subj} {conjugated_verb} {declined_obj}.'

    def make_sentence_for(self, subj: str, verb: str, obj: str, tense: str = 'past') -> str:
        declined_subj = self.decline(subj, 'nom')
        conjugated_verb = self.conjugate(verb, tense, subj)
        declined_obj = self.decline(obj, 'gen')

        return f'{declined_subj} {conjugated_verb} для {declined_obj}.'

    def transliterate_to_russian(self, text: str) -> str:
        original_text = self.clean_name(text).lower()

        if original_text in self.SPECIAL_NAMES:
            return self.SPECIAL_NAMES[original_text]

        result = ''
        i = 0

        while i < len(original_text):
            found = False
            for length in [4, 3, 2, 1]:
                if i + length <= len(original_text):
                    substr = original_text[i:i+length]
                    if substr in self.TRANSLIT_MAP:
                        result += self.TRANSLIT_MAP[substr]
                        i += length
                        found = True
                        break

            if not found:
                result += original_text[i]
                i += 1

        return result.capitalize()

    def transliterate_to_english(self, text: str) -> str:
        result = ''
        for char in text.lower():
            result += self.REVERSE_TRANSLIT_MAP.get(char, char)
        return result.capitalize()

    def add_name(self, name: str, gender: str, cases: Dict[str, str]):
        if gender not in self.NAMES:
            self.NAMES[gender] = {}
        self.NAMES[gender][name] = cases

    def get_all_forms(self, name: str) -> Dict[str, str]:
        gender = self.detect_gender(name)
        cases = ['nom', 'gen', 'dat', 'acc', 'prep']
        return {case: self.decline(name, case, gender) for case in cases}

    def batch_transliterate(self, names: List[str]) -> Dict[str, str]:
        return {name: self.transliterate_to_russian(name) for name in names}

    def conjugate_any_verb(self, verb: str, subject: str, tense: str = 'past') -> str:
        gender = self.detect_gender(subject)
        base_verb = verb.lower().strip()

        if base_verb in self.VERBS:
            return self.conjugate(base_verb, tense, subject)

        if base_verb.endswith('ть'):
            stem = base_verb[:-2]
            if tense == 'past':
                if gender == 'female':
                    return stem + 'ла'
                elif gender == 'male':
                    return stem + 'л'
                else:
                    return stem + 'ло'
            elif tense == 'present':
                if gender in ['male', 'female']:
                    return stem + 'ет'
                return stem + 'ет'

        return verb
