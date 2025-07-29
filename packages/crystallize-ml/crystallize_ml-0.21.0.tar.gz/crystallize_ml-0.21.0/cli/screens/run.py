"""Screen for running experiments and graphs."""

from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, List, Tuple

import networkx as nx
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Header, RichLog, Static
from textual.screen import ModalScreen

from crystallize.experiments.experiment import Experiment
from crystallize.experiments.experiment_graph import ExperimentGraph
from crystallize.plugins.plugins import ArtifactPlugin
from ..status_plugin import CLIStatusPlugin


def _inject_status_plugin(
    obj: Any, callback: Callable[[str, dict[str, Any]], None]
) -> None:
    """Inject CLIStatusPlugin into experiments if not already present."""
    if isinstance(obj, ExperimentGraph):
        for node in obj._graph.nodes:
            exp: Experiment = obj._graph.nodes[node]["experiment"]
            if exp.get_plugin(CLIStatusPlugin) is None:
                exp.plugins.append(CLIStatusPlugin(callback))
    else:
        if obj.get_plugin(CLIStatusPlugin) is None:
            obj.plugins.append(CLIStatusPlugin(callback))


from ..discovery import _run_object
from ..widgets.writer import WidgetWriter
from .delete_data import ConfirmScreen, DeleteDataScreen
from .strategy import StrategyScreen
from .summary import SummaryScreen


class RunScreen(ModalScreen[None]):
    """Display live output of a running experiment."""

    class NodeStatusChanged(Message):
        def __init__(self, node_name: str, status: str) -> None:
            self.node_name = node_name
            self.status = status
            super().__init__()

    class ExperimentComplete(Message):
        def __init__(self, result: Any) -> None:
            self.result = result
            super().__init__()

    BINDINGS = [
        ("ctrl+c", "cancel_and_exit", "Cancel and Go Back"),
        ("q", "cancel_and_exit", "Close"),
    ]

    node_states: dict[str, str] = reactive({})
    replicate_info: str = reactive("")
    progress_percent: float = reactive(0.0)
    step_states: dict[str, str] = reactive({})

    def __init__(self, obj: Any, strategy: str, replicates: int | None) -> None:
        super().__init__()
        self._obj = obj
        self._strategy = strategy
        self._replicates = replicates
        self._result: Any = None

    def watch_node_states(self) -> None:
        if not isinstance(self._obj, ExperimentGraph):
            return
        try:
            dag_widget = self.query_one("#dag-display", Static)
        except NoMatches:
            return
        text = Text(justify="center")
        order = list(nx.topological_sort(self._obj._graph))
        for i, node in enumerate(order):
            status = self.node_states.get(node, "pending")
            style = {
                "completed": "bold green",
                "running": "bold blue",
                "pending": "bold white",
            }.get(status, "bold white")
            text.append(f"[ {node} ]", style=style)
            if i < len(order) - 1:
                text.append(" ⟶  ", style="white")
        dag_widget.update(text)

    def on_node_status_changed(self, message: NodeStatusChanged) -> None:
        self.node_states = {**self.node_states, message.node_name: message.status}

    def watch_step_states(self) -> None:
        if not self.step_states:
            return
        try:
            step_widget = self.query_one("#step-display", Static)
        except NoMatches:
            return
        text = Text(justify="center")
        steps = list(self.step_states.keys())
        for i, step in enumerate(steps):
            status = self.step_states[step]
            style = {
                "completed": "bold green",
                "pending": "bold white",
            }.get(status, "bold white")
            text.append(f"[ {step} ]", style=style)
            if i < len(steps) - 1:
                text.append(" ⟶  ", style="white")
        step_widget.update(text)

    def watch_replicate_info(self) -> None:
        try:
            rep_widget = self.query_one("#replicate-display", Static)
        except NoMatches:
            return
        rep_widget.update(self.replicate_info)

    def watch_progress_percent(self) -> None:
        try:
            prog_widget = self.query_one("#progress-display", Static)
        except NoMatches:
            return
        filled = int(self.progress_percent * 20)
        bar = "[" + "#" * filled + "-" * (20 - filled) + "]"
        prog_widget.update(f"{bar} {self.progress_percent*100:.0f}%")

    def _handle_status_event(self, event: str, info: dict[str, Any]) -> None:
        if event == "start":
            self.step_states = {name: "pending" for name in info.get("steps", [])}
            self.progress_percent = 0.0
            self.replicate_info = "Run started"
        elif event == "replicate":
            rep = info.get("replicate", 0)
            total = info.get("total", 0)
            cond = info.get("condition", "")
            self.replicate_info = f"Replicate {rep}/{total} ({cond})"
            self.step_states = {name: "pending" for name in self.step_states}
        elif event == "step":
            step = info.get("step")
            if step and step in self.step_states:
                self.step_states[step] = "completed"
            self.progress_percent = info.get("percent", 0.0)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="run-container"):
            yield Header(show_clock=True)
            yield Static(f"⚡ Running: {self._obj.name}", id="modal-title")
            yield Static("Run started", id="replicate-display")
            yield Static(id="step-display")
            yield Static(id="progress-display")
            yield Static(id="dag-display", classes="hidden")
            yield RichLog(highlight=True, markup=True, id="live_log")
            yield Button("Close", id="close_run")

    def open_summary_screen(self, result: Any) -> None:
        self.app.push_screen(SummaryScreen(result))

    def status_event(self, event: str, info: dict[str, Any]) -> None:
        """A picklable callback method for the CLIStatusPlugin."""
        self.app.call_from_thread(self._handle_status_event, event, info)

    def on_mount(self) -> None:
        if isinstance(self._obj, ExperimentGraph):
            self.node_states = {node: "pending" for node in self._obj._graph.nodes}
            self.query_one("#dag-display").remove_class("hidden")
        log = self.query_one("#live_log", RichLog)

        _inject_status_plugin(self._obj, self.status_event)

        async def progress_callback(status: str, name: str) -> None:
            self.app.call_from_thread(
                self.on_node_status_changed, self.NodeStatusChanged(name, status)
            )

        def run_experiment_sync() -> None:
            original_stdout = sys.stdout
            sys.stdout = WidgetWriter(log, self.app)
            result = None
            try:

                async def run_with_callback():
                    if isinstance(self._obj, ExperimentGraph):
                        return await self._obj.arun(
                            strategy=self._strategy,
                            replicates=self._replicates,
                            progress_callback=progress_callback,
                        )
                    else:
                        return await _run_object(
                            self._obj, self._strategy, self._replicates
                        )

                result = asyncio.run(run_with_callback())

            except Exception as e:  # pragma: no cover - runtime path
                print(f"[bold red]An error occurred in the worker:\n{e}[/bold red]")
            finally:
                sys.stdout = original_stdout
                self.app.call_from_thread(
                    self.on_experiment_complete, self.ExperimentComplete(result)
                )

        self.worker = self.run_worker(run_experiment_sync, thread=True)

    def on_experiment_complete(self, message: ExperimentComplete) -> None:
        self._result = message.result
        try:
            if self._result is not None:
                self.open_summary_screen(self._result)
            self.query_one("#close_run").remove_class("hidden")
        except NoMatches:  # pragma: no cover - widget missing
            pass

    def action_cancel_and_exit(self) -> None:
        if self.worker and not self.worker.is_finished:
            self.worker.cancel()
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_run":
            self.app.pop_screen()


async def _launch_run(app: App, obj: Any) -> None:
    selected = obj
    if isinstance(selected, ExperimentGraph):
        deletable: List[Tuple[str, Path]] = []
        for node in selected._graph.nodes:
            exp: Experiment = selected._graph.nodes[node]["experiment"]
            plugin = exp.get_plugin(ArtifactPlugin)
            if not plugin or not exp.name:
                continue
            base = Path(plugin.root_dir) / exp.name
            if base.exists():
                deletable.append((node, base))
        if deletable:
            idxs = await app.push_screen_wait(DeleteDataScreen(deletable))
            if idxs is None:
                return
            if idxs:
                paths_to_delete = [deletable[i][1] for i in idxs]
                confirm = await app.push_screen_wait(ConfirmScreen(paths_to_delete))
                if confirm:
                    for p in paths_to_delete:
                        try:
                            shutil.rmtree(p)
                        except OSError:
                            pass
                else:
                    return
    strategy = await app.push_screen_wait(StrategyScreen())
    if strategy is None:
        return
    await app.push_screen(RunScreen(selected, strategy, None))
