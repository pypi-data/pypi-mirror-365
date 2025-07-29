# marmel_grammar/__init__.py
from .grammar import MarmelGrammar
from . import dataset

__version__ = '0.1.8b2'
__author__ = 'Dev-Marmel'
__email__ = 'marmelgpt@gmail.com'
__description__ = 'Библиотека русской морфологии и транслитерации для Python'

__all__ = [
    'MarmelGrammar',
    'dataset',
]
