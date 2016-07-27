from flask import Response
import json

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

def myjsonify(values, detailledJson=False):
    # Transform the structure into a dict
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

    # Don't use jsonsify because jsonify is sorting
    resp = Response(response=json.dumps(values),
                    status=200,
                    mimetype="application/json")
    return(resp)
