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
def validate_cpf(value):
    cpf = ''.join(filter(str.isdigit, str(value)))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido.")

    for i in range(9, 11):
        soma = 0  # Mudei de sum para soma
        for j in range(0, i):
            soma += int(cpf[j]) * ((i + 1) - j)
        rev = (soma * 10) % 11
        if rev == 10 or rev == 11:
            rev = 0
        if rev != int(cpf[i]):
            raise ValidationError("CPF inválido.")

def validate_cnpj(value):
    cnpj = ''.join(filter(str.isdigit, str(value)))

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        raise ValidationError("CNPJ inválido.")

    def calculate_digit(cnpj_parcial, digit):
        if digit == 1:
            weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            length = 12
        else:
            weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            length = 13

        soma = 0
        for i in range(length):
            soma += int(cnpj_parcial[i]) * weights[i]
        rev = soma % 11
        return '0' if rev < 2 else str(11 - rev)

    digit1 = calculate_digit(cnpj, 1)
    digit2 = calculate_digit(cnpj + digit1, 2)

    if cnpj[-2:] != digit1 + digit2:
        raise ValidationError("CNPJ inválido.")