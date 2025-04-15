from enum import Enum

class AwaitingField(Enum):
    NONE = "none"
    AUTHOR_CONFIRMATION = "author_confirmation"
    AUTHOR_EDIT = "author_edit"
    TITLE_CONFIRMATION = "title_confirmation"
    TITLE_EDIT = "title_edit"

user_states = {}
user_data_overrides = {}
