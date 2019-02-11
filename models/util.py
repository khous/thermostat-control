
from flask import jsonify


def to_dict(model):
    my_attrs = model.__dict__.items()
    out_dict = {}

    for attr in my_attrs:
        if attr[0].startswith("_"):
            continue

        out_dict[attr[0]] = attr[1]

    return out_dict