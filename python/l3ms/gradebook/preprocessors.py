import copy as _copy

def _slice(get, scores, start=None, stop=None):
    def compare(score1, score2):
        return cmp(get(score1), get(score2))
    scores = _copy.copy(scores)  # don't upset original order
    scores.sort(compare)
    return scores[start:stop]

def drop_lowest(get, scores, k=1):
    return _slice(get, scores, start=k)

def drop_lowest_2(get, scores):
    return drop_lowest(get, scores, 2)
