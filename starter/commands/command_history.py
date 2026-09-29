"""The invoker of the Command pattern.

Runs commands and keeps the undo/redo stacks.
"""

from commands.transaction_command import Command


class CommandHistory:
    """Executes commands and remembers them for undo and redo.

    Executing a new command clears the redo stack, like in a text editor.
    """

    def __init__(self) -> None:
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(self, command: Command) -> None:
        """Execute ``command`` and make it undoable.

        If the command raises, it is not recorded.
        """
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Undo the most recent command.

        Returns:
            False if there was nothing to undo.
        """
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """Execute the most recently undone command again.

        Returns:
            False if there was nothing to redo.
        """
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return True
