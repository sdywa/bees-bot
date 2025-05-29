from .about import command as about_command
from .greet import command as greet_command
from .main_menu import command as main__menu_command
from .questionnaire import command as questionnaire_command


commands = {
    'about': about_command,
    'greet': greet_command,
    'main_menu': main__menu_command,
    'questionnaire': questionnaire_command,
}