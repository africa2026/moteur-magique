# -*- coding: utf-8 -*-
"""
Multilingual Search Support
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD

Module léger de support multilingue :
- liste des langues supportées par le moteur (IT, FR, EN, ES, PT) ;
- détection heuristique de la langue d'un texte (mots-outils + caractères) ;
- nettoyage/normalisation d'une requête avant recherche.

Aucune dépendance externe : utilisable aussi bien en local que sur Render
(plan gratuit, sans modèle NLP à télécharger).
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Dict, List

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = "it"

# Langues réellement prises en charge par le corpus salesien et les moteurs.
SUPPORTED_LANGUAGES: List[Dict[str, str]] = [
    {"code": "it", "name": "Italiano", "native_name": "Italiano", "default": True},
    {"code": "fr", "name": "Français", "native_name": "Français", "default": False},
    {"code": "en", "name": "English", "native_name": "English", "default": False},
    {"code": "es", "name": "Español", "native_name": "Español", "default": False},
    {"code": "pt", "name": "Português", "native_name": "Português", "default": False},
]

# Mots-outils discriminants (volontairement courts et fréquents).
_STOPWORDS: Dict[str, tuple] = {
    "it": (
        "il", "lo", "la", "gli", "le", "di", "del", "della", "dei", "che",
        "e", "è", "un", "una", "per", "con", "non", "sono", "come", "più",
        "questo", "questa", "anche", "nel", "nella", "si", "ma", "dal",
    ),
    "fr": (
        "le", "la", "les", "des", "du", "de", "et", "est", "un", "une",
        "pour", "avec", "non", "sont", "comme", "plus", "ce", "cette",
        "aussi", "dans", "se", "mais", "au", "aux", "qui", "que",
    ),
    "en": (
        "the", "of", "and", "is", "are", "to", "in", "for", "with", "not",
        "this", "that", "as", "more", "also", "was", "were", "by", "on",
        "from", "which", "who", "it",
    ),
    "es": (
        "el", "la", "los", "las", "de", "del", "y", "es", "un", "una",
        "para", "con", "no", "son", "como", "más", "este", "esta", "también",
        "en", "se", "pero", "que", "por",
    ),
    "pt": (
        "o", "a", "os", "as", "de", "do", "da", "e", "é", "um", "uma",
        "para", "com", "não", "são", "como", "mais", "este", "esta", "também",
        "em", "se", "mas", "que", "por",
    ),
}

# Indices non ambigus (caractères/accent typiques d'une langue).
_LANGUAGE_HINTS: Dict[str, tuple] = {
    "it": ("ità", "zione", "gli", "è", "ò", "ù"),
    "fr": ("é", "è", "ê", "ç", "qu'", "aujourd", "œuvre", "système"),
    "es": ("ñ", "ción", "qué", "cómo", "también", "educación"),
    "pt": ("ã", "õ", "ção", "não", "educação"),
}

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def get_supported_languages() -> List[Dict[str, str]]:
    """Retourne la liste des langues supportées (utilisé par /api/languages)."""
    return [dict(lang) for lang in SUPPORTED_LANGUAGES]


def get_default_language() -> str:
    """Retourne le code de la langue par défaut."""
    return DEFAULT_LANGUAGE


def is_supported_language(code: str) -> bool:
    """Indique si un code de langue est supporté."""
    return bool(code) and code.lower() in {lang["code"] for lang in SUPPORTED_LANGUAGES}


def detect_language(text: str) -> str:
    """
    Détecte la langue d'un texte par comptage de mots-outils et d'indices
    typographiques. Retourne le code de langue détecté, ou la langue par
    défaut si le texte est trop court/ambigu.
    """
    if not text or not text.strip():
        return DEFAULT_LANGUAGE

    normalized = unicodedata.normalize("NFC", text).lower()
    words = _WORD_RE.findall(normalized)

    if not words:
        return DEFAULT_LANGUAGE

    scores: Dict[str, float] = {code: 0.0 for code in _STOPWORDS}

    for word in words:
        for code, stopwords in _STOPWORDS.items():
            if word in stopwords:
                scores[code] += 1.0

    for code, hints in _LANGUAGE_HINTS.items():
        for hint in hints:
            if hint in normalized:
                # Les indices typographiques pèsent peu : ils tranchent les égalités.
                scores[code] += 0.5

    best_code = max(scores, key=lambda code: scores[code])
    if scores[best_code] <= 0:
        return DEFAULT_LANGUAGE

    return best_code


def normalize_query(query: str) -> str:
    """
    Normalise une requête avant envoi aux moteurs : espaces multiples,
    caractères de contrôle, ponctuation isolée en fin de chaîne.
    """
    if not query:
        return ""

    cleaned = unicodedata.normalize("NFC", str(query))
    cleaned = re.sub(r"[\u0000-\u001f\u007f]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.strip(" ,;:-–—")

    return cleaned
