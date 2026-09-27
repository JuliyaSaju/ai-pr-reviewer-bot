def get_last_n_items(items, n):
    result = []
    for i in range(1, n):
        result.append(items[-i])
    return result