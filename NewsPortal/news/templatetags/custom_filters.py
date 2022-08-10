from django import template

register = template.Library()

UNWANTED_WORD = ["Полузащитник", "ПСЖ", "Ибрагимович", "Левандовски"]


@register.filter()
def censor(value):
    for i in UNWANTED_WORD:
        if i in value:
            value = value.replace(i, i[:1] + ("*" * (len(i) - 1)))
    return f'{value}'