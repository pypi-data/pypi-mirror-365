import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomPasswordValidator:
    """
    Validates that a password meets the following criteria:
    - At least 10 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    - Does not contain user's email, first name, or last name
    """

    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("This password is too short. It must contain at least 8 characters."),
                code='password_too_short',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_uppercase',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code='password_no_lowercase',
            )

        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("This password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special',
            )

        if user:
            email = user.email.lower() if user.email else ''
            first_name = user.first_name.lower() if user.first_name else ''
            last_name = user.last_name.lower() if user.last_name else ''
            password_lower = password.lower()

            if email and email in password_lower:
                raise ValidationError(
                    _("The password cannot contain your email address."),
                    code='password_contains_email',
                )
            if first_name and first_name in password_lower:
                raise ValidationError(
                    _("The password cannot contain your first name."),
                    code='password_contains_first_name',
                )
            if last_name and last_name in password_lower:
                raise ValidationError(
                    _("The password cannot contain your last name."),
                    code='password_contains_last_name',
                )

    def get_help_text(self):
        return _(
            "Your password must be at least 10 characters long and include an uppercase letter, "
            "a lowercase letter, a digit, and a special character. It must not contain your name or email address."
        )