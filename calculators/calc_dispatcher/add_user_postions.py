class AddUserPositions:
    def __init__(self, moduls, user_positions: tuple = ()):
        # добавляемые пользователем позиции проверяются в validate_user_positions
        if user_positions:
            self._moduls = moduls
            self._user_postions = user_positions
            self.add_postions()

    def add_postions(self):
        for pos in self._user_postions:
            self._moduls["options"].append(pos)
