"""Screen for selecting run strategy and artifacts to delete."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static, SelectionList
from textual.widgets.selection_list import Selection

from .selection_screens import ActionableSelectionList, SingleSelectionList


class PrepareRunScreen(ModalScreen[tuple[str, tuple[int, ...]] | None]):
    """Collect execution strategy and deletable artifacts."""

    CSS_PATH = "style/prepare_run.tcss"

    BINDINGS = [
        ("ctrl+c", "cancel_and_exit", "Cancel"),
        ("escape", "cancel_and_exit", "Cancel"),
        ("q", "cancel_and_exit", "Close"),
    ]

    def __init__(self, deletable: List[Tuple[str, Path]]) -> None:
        super().__init__()
        self._deletable = deletable
        self._strategy: str | None = None

    def compose(self) -> ComposeResult:
        with Container(id="prepare-run-container"):
            yield Static("Configure Run", id="modal-title")
            self.options = SingleSelectionList(
                Selection("resume", "resume", id="resume"),
                Selection("rerun", "rerun", id="rerun"),
                id="run-method",
            )
            yield self.options
            if self._deletable:
                yield Static("Select data to delete (optional)", id="delete-info")
                self.list = ActionableSelectionList(classes="invisible")
                for idx, (name, path) in enumerate(self._deletable):
                    self.list.add_option(Selection(f"  {name}: {path}", idx))
                yield self.list
            with Horizontal(classes="button-row"):
                yield Button("Run", variant="success", id="run")
                yield Button("Cancel", variant="error", id="cancel")
            yield Static(id="run-feedback")

    def on_mount(self) -> None:
        self.options.focus()

    def on_selection_list_selected_changed(
        self, message: SelectionList.SelectedChanged
    ) -> None:
        if message.selection_list.selected:
            self._strategy = str(message.selection_list.selected[0])
            if self._strategy == "resume":
                self.list.remove_class("invisible")
            else:
                self.list.add_class("invisible")

    def on_actionable_selection_list_submitted(
        self, message: ActionableSelectionList.Submitted
    ) -> None:
        if self._strategy is not None:
            self.dismiss((self._strategy, message.selected))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            if self._strategy is None:
                self.query_one("#run-feedback", Static).update(
                    f"[red]Select a run strategy to continue[/red]"
                )
                return
            selections: tuple[int, ...] = ()
            if hasattr(self, "list"):
                selections = tuple(v for v in self.list.selected if isinstance(v, int))
            self.dismiss((self._strategy, selections))
        else:
            self.dismiss(None)

    def action_cancel_and_exit(self) -> None:
        self.dismiss(None)
