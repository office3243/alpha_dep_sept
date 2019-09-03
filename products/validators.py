from django.core.validators import ValidationError


def validate_nonzero(value):
    if value < 1:
        raise ValidationError(
            'Value cannot be less than 1'
        )

#
# def validate_nonzero(value):
#     if value < 1:
#         raise ValidationError(
#             'Value cannot be less than 1'
#         )
