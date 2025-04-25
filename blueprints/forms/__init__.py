import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

forms_bp = Bluelogger.debug('forms', __name__, url_prefix='/forms')

from . import routes