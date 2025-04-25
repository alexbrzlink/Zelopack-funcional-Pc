from datetime import datetime
from app import db

class Report(db.Model):
    """Modelo para armazenar informações sobre laudos."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Tamanho em bytes
    category = db.Column(db.String(100), nullable=True)
    supplier = db.Column(db.String(150), nullable=True)
    batch_number = db.Column(db.String(100), nullable=True)
    report_date = db.Column(db.Date, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report {self.id}: {self.title}>"
    
    def to_dict(self):
        """Converte objeto para dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'category': self.category,
            'supplier': self.supplier,
            'batch_number': self.batch_number,
            'report_date': self.report_date.strftime('%d/%m/%Y') if self.report_date else None,
            'upload_date': self.upload_date.strftime('%d/%m/%Y %H:%M'),
            'updated_date': self.updated_date.strftime('%d/%m/%Y %H:%M')
        }


class Category(db.Model):
    """Modelo para categorias de laudos."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Supplier(db.Model):
    """Modelo para fornecedores relacionados aos laudos."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    contact = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f"<Supplier {self.name}>"
