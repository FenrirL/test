def update_active_langs(result, active_langs):
    orig_lang = result.get('language')
    if orig_lang and orig_lang not in active_langs:
        active_langs.insert(0, orig_lang)
    return active_langs