"""добавление пользователских примечаний"""


class AddNotes:
    def __init__(self, moduls, notes=None):
        if notes:
            self._moduls = moduls
            self._notes = notes
            self._moduls["notes"] = [note for note in notes]
