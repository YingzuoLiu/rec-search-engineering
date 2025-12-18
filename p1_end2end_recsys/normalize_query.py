def normalize_query(query, slang_map):
    # 1. lowercase + trim spaces
    q = query.lower().strip()

    # 2. split into tokens
    tokens = q.split()

    # 3. replace slang tokens if needed
    norm_tokens = []
    for t in tokens:
        if t in slang_map:
            norm_tokens.append(slang_map[t])
        else:
            norm_tokens.append(t)

    # 4. join back to string
    return " ".join(norm_tokens)
