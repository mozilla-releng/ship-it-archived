from flask import Response
import json

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def jsonify_by_sorting_values(values, detailledJson=False):
    values = OrderedDict(values)

    if detailledJson:
        # But when this is done on the new json files, it has to be done on
        # the releases member
        valuesToOrder = values["releases"]
    else:
        valuesToOrder = values

    valuesOrdered = OrderedDict(sorted(valuesToOrder.items(), key=lambda x: x[1]))

    if detailledJson:
        values["releases"] = valuesOrdered
    else:
        values = valuesOrdered

    return _craft_response(json.dumps(values))


def jsonify_by_sorting_keys(values):
    return _craft_response(json.dumps(values, sort_keys=True, indent=4))


def _craft_response(json_value):
    resp = Response(response=json_value,
                    status=200,
                    mimetype="application/json")
    return(resp)
