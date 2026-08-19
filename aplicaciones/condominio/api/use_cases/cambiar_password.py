from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class CambiarPasswordUseCase:

    @staticmethod
    def execute(user, password_actual, password_nueva):

        # 1. Validar password actual
        if not user.check_password(password_actual):
            raise ValidationError({
                'password_actual': 'La contraseña actual no es correcta.'
            })

        # 2. Validar nueva password con los validadores de Django
        try:
            validate_password(password_nueva, user)
        except ValidationError as e:
            raise ValidationError({
                'password_nueva': e.messages
            })

        # 3. Cambiar password
        user.set_password(password_nueva)
        user.save(update_fields=['password'])

        return user