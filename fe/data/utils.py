import jieba


def cut_word(text):
    stopwords = [
        "―",
        "“",
        "”",
        "。",
        "    ",
        ".",
        "'",
        "，",
        "\n",
        "]",
        "[",
        "·",
        "(",
        ")",
        "（",
        "）",
        "；",
        "...",
        "......",
    ]
    if text != None:
        text_cutted = jieba.cut(str(text))  # jieba
        words = [word for word in text_cutted if word not in stopwords]
        return words

def gen__t(book_dict):
    _t_insert = []
    attrs = ['title', 'author', 'tags', 'author_intro', 'book_intro', 'content']
    for attr in attrs:
        text = book_dict[attr]
        if text != None:
            _t_insert.extend(cut_word(text))
    return ' '.join(_t_insert)

