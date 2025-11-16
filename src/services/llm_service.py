from src.common.const import E_KEYS, N_KEYS, L_KEYS


class LLMService:
    def __init__(self):
        pass

    def _score_scale(self, responses: list[bool], keys: list[int]) -> int:
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

    def score_epi(self, responses: list[bool]) -> dict[str, object]:
        """Возвращает словарь с баллами."""
        e = self._score_scale(responses, E_KEYS)
        n = self._score_scale(responses, N_KEYS)
        l = self._score_scale(responses, L_KEYS)

        res = {
            "E_raw": e,
            "E_max": len(E_KEYS),
            "N_raw": n,
            "N_max": len(N_KEYS),
            "L_raw": l,
            "L_max": len(L_KEYS),
        }

        interp = []
        # Lie scale: обычно L >= 5 → вероятна социально-желательная искаженность ответов
        if l >= 5:
            interp.append(
                f"Lie scale {l}/{res['L_max']}: возможна попытка выглядеть лучше (ответы могут быть искажены)."
            )
        else:
            interp.append(
                f"Lie scale {l}/{res['L_max']}: нет сильных признаков фальсификации."
            )

        # Extraversion
        interp.append(
            f"E (Extraversion): {e}/{res['E_max']} (чем выше — более экстравертированы)."
        )

        # Neuroticism
        interp.append(
            f"N (Neuroticism): {n}/{res['N_max']} (чем выше — более невротичны)."
        )

        res["interpretation"] = interp
        return res
