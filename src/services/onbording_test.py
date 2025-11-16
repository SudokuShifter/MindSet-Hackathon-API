from typing import List, Dict

# Ключи EPI
E_KEYS = [  1,  3, -5,  8, 10, 13, -15, 17, -20, 22, 25, 27, -29, -32, -34, -37,
           39, -41, 44, 46, 49, -51, 53, 56 ]   
N_KEYS = [  2,  4,  7,  9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38,
           40, 43, 45, 47, 50, 52, 55, 57 ] 
L_KEYS = [  6, -12, -18, 24, -30, 36, -42, -48, -54 ] 

def score_scale(responses: List[bool], keys: List[int]) -> int:
    """Считает баллы по одной шкале.
    responses: список длины 57 (True/False), номера вопросов 1..57 соответствуют индексам 0..56.
    keys: список целых: положительное -> 'Yes' даёт балл; отрицательное -> 'No' даёт балл.
    """
    if len(responses) != 57:
        raise ValueError("Ожидается список длины 57 (пункты 1..57).")
    score = 0
    for k in keys:
        idx = abs(k) - 1
        ans = responses[idx]
        if k > 0 and ans is True:
            score += 1
        if k < 0 and ans is False:
            score += 1
    return score

def score_epi(responses: List[bool]) -> Dict[str, object]:
    """Возвращает словарь с баллами."""
    e = score_scale(responses, E_KEYS)
    n = score_scale(responses, N_KEYS)
    l = score_scale(responses, L_KEYS)

    res = {
        "E_raw": e,
        "E_max": len(E_KEYS),
        "N_raw": n,
        "N_max": len(N_KEYS),
        "L_raw": l,
        "L_max": len(L_KEYS)
    }

    interp = []
    # Lie scale: обычно L >= 5 → вероятна социально-желательная искаженность ответов
    if l >= 5:
        interp.append(f"Lie scale {l}/{res['L_max']}: возможна попытка выглядеть лучше (ответы могут быть искажены).")
    else:
        interp.append(f"Lie scale {l}/{res['L_max']}: нет сильных признаков фальсификации.")

    # Extraversion
    interp.append(f"E (Extraversion): {e}/{res['E_max']} (чем выше — более экстравертированы).")

    # Neuroticism
    interp.append(f"N (Neuroticism): {n}/{res['N_max']} (чем выше — более невротичны).")

    res["interpretation"] = interp
    return res
