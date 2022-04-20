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
    return jsonify(repr(document_row)), 200

@documents.route('', methods=['GET'])
@utils.server_error_check
@utils.authorize_user
def get_documents(payload):
    # print(payload)
    user_id_from_authorization_header = payload['user_id']
    args = request.args
    user_id = args.get('user_id')
    if user_id != user_id_from_authorization_header:
        return jsonify({'message':'unauthorized request.'}), 400
    document_id_array = state_machine.get_all_documents_by_user_id(user_id)
    return jsonify(document_id_array), 200