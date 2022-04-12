import documents.state_machine as state_machine
import documents.decorators as decorators
from flask import jsonify, request, Blueprint

documents = Blueprint("documents", __name__, template_folder="templates")

@documents.route('', methods=['POST'])
@decorators.utils
@decorators.auth
def upsert_documents(payload):
    user_id = payload['userid']
    state_machine.get_user_by_user_id(user_id)
    document_id = state_machine.upsert_document(user_id)
    document_row = state_machine.get_document_by_id(document_id)
    return jsonify(repr(document_row)), 200

@documents.route('', methods=['GET'])
@decorators.utils
def get_documents():
    args = request.args
    user_id = args.get('user_id')
    if user_id == "" or user_id == None:
        return jsonify({'message':'user_id not entered.'}), 400
    document_id_array = state_machine.get_all_documents_by_user_id(user_id)
    return jsonify(document_id_array), 200