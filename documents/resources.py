import documents.state_machine as state_machine
from sendgrid_helper import send_invite_email
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
        return jsonify({'message':'unauthorized request.'}), 403
    email = state_machine.get_user_by_user_id(user_id)['email']
    documents_array = state_machine.get_all_documents_by_user_id(user_id, email)
    return jsonify(documents_array), 200

@documents.route('/<document_id>', methods=['POST'])
@utils.server_error_check
@utils.authorize_user
def update_documents(document_id, payload):
    data = request.get_json()
    data_from_user = data['data']
    user_id_from_document_id = str(state_machine.get_document_by_id(document_id).user_id)
    user_id_from_authorization_header = payload['user_id']
    if user_id_from_authorization_header != user_id_from_document_id:
        email_from_user_id = state_machine.get_user_by_user_id(user_id_from_authorization_header)['email']
        shared_document_row = state_machine.get_shared_document_by_id_and_email(document_id, email_from_user_id)
        if shared_document_row is None:
            return jsonify({'message':'unauthorized request.'}), 403
    if data_from_user == "" or data_from_user == None:
        jsonify({'message':'Data updated already.'}), 400
    if 'name' in data:
        state_machine.update_document_by_document_id(document_id, data_from_user, data['name'])
    else:
        state_machine.update_document_data_by_document_id(document_id, data_from_user)
    return jsonify({'message':'Data saved.'}), 200

@documents.route('/<document_id>', methods=['GET'])
@utils.server_error_check
def get_document_data(document_id):
    document_row = state_machine.get_document_by_id(document_id)
    user_id_from_document_row = str(document_row.user_id)
    document_owner_email = state_machine.get_user_by_user_id(user_id_from_document_row)['email']
    owner_shared_document_row = state_machine.get_shared_document_by_id_and_email(document_id, document_owner_email)
    if owner_shared_document_row is not None:
        if owner_shared_document_row.public == True:
                return jsonify(document_row.__serialize__()), 200
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({'message':'unauthorized request.'}), 403
    payload = utils.token_valid_check(auth_header)
    user_id_from_authorization_header = payload['user_id']
    if user_id_from_authorization_header == user_id_from_document_row:
        return jsonify(document_row.__serialize__()), 200
    email_from_user_id = state_machine.get_user_by_user_id(user_id_from_authorization_header)['email']
    shared_document_row = state_machine.get_shared_document_by_id_and_email(document_id, email_from_user_id)
    if shared_document_row is not None:
        return jsonify(document_row.__serialize__()), 200
    else:
        return jsonify({'message':'unauthorized request.'}), 403

@documents.route('/<document_id>', methods=['DELETE'])
@utils.server_error_check
@utils.authorize_user
def delete_document(document_id,payload):
    user_id = payload['user_id']
    user_id_from_document_row = str(state_machine.get_document_by_id(document_id).user_id)
    if user_id != user_id_from_document_row:
        return jsonify({'message':'unauthorized request.'}), 403
    state_machine.delete_document(document_id)
    return jsonify({"message":"Document deleted."}), 200

@documents.route('/<document_id>/share', methods=['POST'])
@utils.server_error_check
@utils.authorize_user
def share_document(document_id, payload):
    data = request.get_json()
    shared_user_email = data['email'] 
    user_id = payload['user_id']
    document_row = state_machine.get_document_by_id(document_id)
    if user_id != str(document_row.user_id):
        return jsonify({'message':'unauthorized request.'}), 403
    shared_document_row = state_machine.get_shared_document_by_id_and_email(document_id, shared_user_email)
    if shared_document_row is not None:
        if 'public' in data:
            state_machine.update_shared_document(document_id, shared_user_email, data['public'])
            return jsonify({'message':'updated shared document.'})
        return jsonify({'message':'document shared already.'}), 400
    user_row = state_machine.get_user_by_email(shared_user_email)
    if user_row is None:
        send_invite_email(shared_user_email)
    if 'public' in data:
        state_machine.upsert_shared_document_with_public(document_id, shared_user_email, data['public'])    
    else:
        state_machine.upsert_shared_document(document_id, shared_user_email)    
    return jsonify({'message':'Document shared.'}), 200