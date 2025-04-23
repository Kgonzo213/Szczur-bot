from random import choice, randint
import re


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Co tam szczurzysz pod nosem?'
    elif 'cześć' in lowered or 'siemia' in lowered or 'hej' in lowered:
        return 'Witam Szczurzeeeeeeee'
    elif re.search(r'\bszczur\w*', lowered):  
        return 'Szczurzeeeeeeeeeeeeeeee!'
    else:
        return ''