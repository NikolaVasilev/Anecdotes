from django.utils.safestring import mark_safe

from Anecdotes.models import Reactions


def generate_icon_html(icon, color=None):
    html_code = icon
    if color is not None:
        color = f'style="color:{color}"'
        string = html_code.split('>', 1)[0]
        html_code = string + color + '></i>'

    return mark_safe(html_code)


def generate_reactions_table(obj):
    html = ''
    html += '<table><tr>'
    for reaction in obj.reactions_details:
        html += '<th>' + reaction['reaction__name']+'</th>'
    html += '</tr>'
    for reaction in obj.reactions_details:
        html += '<td style="text-align:center">' + generate_icon_html(reaction['reaction__icon'], color=reaction['reaction__color']) + ' : ' + str(reaction['count']) + '</td> '
    html += '</table>'
    return mark_safe(html)


def is_reaction_exist(reaction_id, user_id, anecdote_id):
    try:
        Reactions.objects.get(
            reaction_id=reaction_id,
            user_id=user_id,
            anecdote_id=anecdote_id)
        return True

    except Reactions.DoesNotExist:
        return False
