from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValidationError("O arquivo não pode exceder 10MB.")

def validate_file_mimetype(value):
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif','dwg']
    ext = value.name.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError("Extensão inválida. Use apenas PDF, JPG, PNG ou GIF.")
