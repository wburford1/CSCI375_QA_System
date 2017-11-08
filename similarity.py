def cosine_similarity(vector1, vector2):
    assert len(vector1) == len(vector2)
    dot_prod = sum([vector1[i]*vector2[i] for i in range(0, len(vector1), 1)])
    mag1_squared = sum([vector1[i]**2 for i in range(0, len(vector1), 1)])
    mag2_squared = sum([vector2[i]**2 for i in range(0, len(vector2), 1)])
    return dot_prod / ((mag1_squared * mag2_squared)**(1/2))
