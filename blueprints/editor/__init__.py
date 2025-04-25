from flask import Blueprint

editor_bp = Blueprint('editor', __name__, url_prefix='/editor', 
                     template_folder='templates')

from blueprints.editor import routes