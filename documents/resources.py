import documents.state_machine as state_machine
from flask import jsonify, request, Blueprint

documents = Blueprint("documents", __name__, template_folder="templates")

@documents.route('/documents', methods=['POST'])
def upsert_documents():
    try:
        auth_header = request.headers.get('Authorization')            
        payload = state_machine.token_valid_check(auth_header)
        user_id = payload['userid']
        state_machine.get_user_by_user_id(user_id)
        document_id = state_machine.upsert_document(user_id)
        document_row = state_machine.get_document_by_id(document_id)
        return jsonify(repr(document_row)), 200
    except Exception as e:
        return jsonify({str(e.message)}), 500

@documents.route('/documents', methods=['GET'])
def get_documents():
    try:
        args = request.args
        user_id = args.get('user_id')
        if user_id == "" or user_id == None:
            return jsonify({'message':'user_id not entered.'}), 400
        document_id_array = state_machine.get_all_documents_by_user_id(user_id)
        return jsonify(document_id_array), 200
    except:
        return jsonify({'message':'Invalid user_id.'}), 500