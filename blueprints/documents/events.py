"""
Eventos em tempo real para o editor de documentos.
"""
from flask_socketio import emit, join_room, leave_room
from flask import request
from app import socketio
import logging

# Dicionário para armazenar o estado dos documentos em edição
documents_in_edit = {}

# Dicionário para acompanhar usuários conectados a cada documento
connected_users = {}

@socketio.on('connect')
def handle_connect():
    """Evento quando um cliente se conecta ao Socket.IO."""
    logging.debug("Cliente conectado ao Socket.IO")

@socketio.on('disconnect')
def handle_disconnect():
    """Evento quando um cliente se desconecta do Socket.IO."""
    logging.debug("Cliente desconectado do Socket.IO")
    
    # Remover usuário de documentos em que estava editando
    for doc_id, users in list(connected_users.items()):
        if users and request.sid in users:
            users.remove(request.sid)
            # Se não houver mais usuários, podemos limpar esse documento
            if not users:
                if doc_id in documents_in_edit:
                    del documents_in_edit[doc_id]
                del connected_users[doc_id]
            else:
                # Notificar outros usuários que este saiu
                emit('user_left', {'sid': request.sid}, room=doc_id)

@socketio.on('join_document')
def handle_join_document(data):
    """Evento quando um usuário começa a editar um documento."""
    doc_id = data.get('document_id', 'default_doc')
    user_info = data.get('user_info', {})
    
    # Juntar-se à sala específica para este documento
    join_room(doc_id)
    
    # Adicionar usuário à lista de conectados neste documento
    if doc_id not in connected_users:
        connected_users[doc_id] = []
    
    # Adicionar este cliente com informações do usuário
    user_data = {
        'sid': request.sid,
        'name': user_info.get('name', 'Anônimo'),
        'color': user_info.get('color', '#007bff')
    }
    connected_users[doc_id].append(user_data)
    
    # Notificar outros usuários que um novo usuário se juntou
    emit('user_joined', user_data, room=doc_id, include_self=False)
    
    # Enviar a lista atual de usuários para o cliente que acabou de se conectar
    emit('current_users', {'users': connected_users.get(doc_id, [])})
    
    # Enviar o conteúdo atual do documento para o novo usuário
    if doc_id in documents_in_edit:
        emit('load_content', {'content': documents_in_edit[doc_id]})

@socketio.on('leave_document')
def handle_leave_document(data):
    """Evento quando um usuário para de editar um documento."""
    doc_id = data.get('document_id', 'default_doc')
    
    # Sair da sala
    leave_room(doc_id)
    
    # Remover usuário da lista de editores
    if doc_id in connected_users:
        # Filtrar a lista para remover este cliente
        connected_users[doc_id] = [u for u in connected_users[doc_id] if u.get('sid') != request.sid]
        
        # Se não houver mais usuários, podemos limpar esse documento
        if not connected_users[doc_id]:
            if doc_id in documents_in_edit:
                del documents_in_edit[doc_id]
            del connected_users[doc_id]
        else:
            # Notificar outros usuários que este saiu
            emit('user_left', {'sid': request.sid}, room=doc_id)

@socketio.on('update_content')
def handle_update_content(data):
    """Evento quando o conteúdo do documento é atualizado."""
    doc_id = data.get('document_id', 'default_doc')
    content = data.get('content', '')
    user_id = data.get('user_id', '')
    
    # Atualizar o conteúdo armazenado
    documents_in_edit[doc_id] = content
    
    # Broadcast para todos os clientes conectados a este documento, exceto o remetente
    emit('content_updated', {
        'content': content, 
        'user_id': user_id
    }, room=doc_id, include_self=False)

@socketio.on('cursor_move')
def handle_cursor_move(data):
    """Evento quando um usuário move o cursor no documento."""
    doc_id = data.get('document_id', 'default_doc')
    position = data.get('position', {})
    user_id = data.get('user_id', '')
    
    # Broadcast para todos os clientes conectados a este documento, exceto o remetente
    emit('cursor_update', {
        'position': position,
        'user_id': user_id
    }, room=doc_id, include_self=False)

@socketio.on('selection_change')
def handle_selection_change(data):
    """Evento quando um usuário seleciona texto no documento."""
    doc_id = data.get('document_id', 'default_doc')
    selection = data.get('selection', {})
    user_id = data.get('user_id', '')
    
    # Broadcast para todos os clientes conectados a este documento, exceto o remetente
    emit('selection_update', {
        'selection': selection,
        'user_id': user_id
    }, room=doc_id, include_self=False)