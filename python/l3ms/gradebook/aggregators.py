def sum(get_points, scores):
    n = 0
    for s in scores:
        n += get_points(s)
    return n
