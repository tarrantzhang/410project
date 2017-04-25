from flask import Flask, request, jsonify, Response
import logging
import os
import json


logger = logging.getLogger(__name__)

app = Flask('Assembo')


@app.errorhandler(404)
def not_found(error=None):
    """
    Returns 404 Status Code with reason being 'Not Found'.

    Inspiration from http://blog.luisrei.com/articles/flaskrest.html
    :param error: The error.
    :return: Response with 404 status code.
    """
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


# Example function.
@app.route('/api/<string:name>/<string:age>', methods=['GET'])
def test(name, age):
    if name == 'NULL':
        return not_found()

    data = json.dumps({
        'name': name,
        'age': age,
    })

    return Response(data, status=200, mimetype='application/json');


if __name__ == '__main__':
    app.run(debug=True)
