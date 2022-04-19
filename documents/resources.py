import documents.state_machine as state_machine
import utils
from flask import jsonify, request, Blueprint

documents = Blueprint("documents", __name__, template_folder="templates")

@documents.route('', methods=['POST'])
@utils.server_error_check
@utils.authenticate_user
def upsert_documents(payload):
    user_id = payload['userid']
    state_machine.get_user_by_user_id(user_id)
    document_row = state_machine.upsert_document(user_id)
    return jsonify(repr(document_row)), 200

@documents.route('', methods=['GET'])
@utils.server_error_check
@utils.authenticate_user
def get_documents():
    # print(payload)
    args = request.args
    user_id = args.get('user_id')
    document_id_array = state_machine.get_all_documents_by_user_id(user_id)
    return jsonify(document_id_array), 200