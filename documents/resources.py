import documents.state_machine as state_machine
import utils
from flask import jsonify, request, Blueprint

documents = Blueprint("documents", __name__, template_folder="templates")

@documents.route('', methods=['POST'])
@utils.server_error_check
@utils.authorize_user
def upsert_documents(payload):
    user_id = payload['user_id']
    state_machine.get_user_by_user_id(user_id)
    document_row = state_machine.upsert_document(user_id)
    return jsonify(document_row.__serialize__()), 200

@documents.route('', methods=['GET'])
@utils.server_error_check
@utils.authorize_user
def get_documents(payload):
    user_id_from_authorization_header = payload['user_id']
    args = request.args
    user_id = args.get('user_id')
    if user_id != user_id_from_authorization_header:
        return jsonify({'message':'unauthorized request.'}), 400
    document_id_array = state_machine.get_all_documents_by_user_id(user_id)
    return jsonify(document_id_array), 200

@documents.route('/<document_id>', methods=['POST'])
@utils.server_error_check
@utils.authorize_user
def update_documents(document_id, payload):
    data = request.get_json()
    data_from_user = data['data']
    user_id_from_authorization_header = payload['user_id']
    user_id_from_document_id = str(state_machine.get_document_by_id(document_id).user_id)
    if user_id_from_authorization_header != user_id_from_document_id:
        return jsonify({'message':'unauthorized request.'}), 400
    if data_from_user == "" or data_from_user == None:
        jsonify({'message':'Data updated already.'}), 400
    if 'name' in data:
        state_machine.update_document_by_document_id(document_id, data_from_user, data['name'])
    else:
        state_machine.update_document_data_by_document_id(document_id, data_from_user)
    return jsonify({'message':'Data saved.'}), 200

@documents.route('/<document_id>', methods=['GET'])
@utils.server_error_check
@utils.authorize_user
def get_document_data(document_id, payload):
    user_id_from_authorization_header = payload['user_id']
    document_row = state_machine.get_document_by_id(document_id)
    user_id_from_document_id = str(document_row.user_id)
    if user_id_from_authorization_header != user_id_from_document_id:
        return jsonify({'message':'unauthorized request.'}), 400
    return jsonify(document_row.__serialize__()), 200