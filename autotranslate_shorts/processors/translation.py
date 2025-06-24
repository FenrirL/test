from typing import List

def translate_sentences(sentences: List[str], target_lang: str) -> List[str]:
    """
    Traduction stub (à remplacer par Argos, DeepL, etc.)
    """
    # TODO: Appel DeepTranslator/Argos ou API selon settings
    return [s + f" [{target_lang}]" for s in sentences]