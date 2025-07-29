"""Screens for confirming deletion of artifacts."""

from __future__ import annotations

from pathlib import Path


from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Static
from textual.screen import ModalScreen



class ConfirmScreen(ModalScreen[bool]):
    BINDINGS = [
        ("ctrl+c", "cancel_and_exit", "Cancel"),
        ("y", "confirm_and_exit", "Confirm"),
        ("n", "cancel_and_exit", "Cancel"),
    ]

    def __init__(self, paths_to_delete: list[Path]) -> None:
        super().__init__()
        self._paths = paths_to_delete

    def compose(self) -> ComposeResult:
        with Container(classes="confirm-delete-container"):
            yield Static(
                "[bold red]The following will be permanently deleted:[/bold red]"
            )
            with VerticalScroll(classes="path-list"):
                if not self._paths:
                    yield Static("  (Nothing selected)")
                for path in self._paths:
                    yield Static(f"• {path}")
            yield Static("\nAre you sure you want to proceed? (y/n)")
            yield Horizontal(
                Button("Yes, Delete", variant="error", id="yes"),
                Button("No, Cancel", variant="primary", id="no"),
            )

    def on_mount(self) -> None:
        self.query_one("#no", Button).focus()

    def action_confirm_and_exit(self) -> None:
        self.dismiss(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def action_cancel_and_exit(self) -> None:
        self.dismiss(False)
