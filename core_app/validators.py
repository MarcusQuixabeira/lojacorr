import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_cpf(value: str):
    """
    Checks if a cpf is valid
    
    Args:
      value:str cpf to be evaluated
    """
    digits = re.sub(r'\D', '', value or '')
    if len(digits) != 11:
        raise ValidationError(_('CPF needs to have 11 characters'))
    if digits == digits[0] * 11:
        raise ValidationError(_('Invalid CPF'))

    def calc_dv(nums: str, start_weight: int) -> str:
        s = sum(int(n) * w for n, w in zip(nums, range(start_weight, 1, -1)))
        r = s % 11
        return '0' if r < 2 else str(11 - r)

    dv1 = calc_dv(digits[:9], 10)
    dv2 = calc_dv(digits[:9] + dv1, 11)

    if digits[-2:] != dv1 + dv2:
        raise ValidationError(_('Invalid CPF'))