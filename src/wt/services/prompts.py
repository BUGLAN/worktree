from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Generic, TypeVar

from wt.errors import UserFacingError

T = TypeVar("T")


class PromptIO(Generic[T]):
    def ask_text(self, label: str) -> str:
        value = input(f"{label}: ").strip()
        if not value:
            raise UserFacingError(f"{label} is required.")
        return value

    def confirm(self, label: str, default: bool = True) -> bool:
        suffix = "[Y/n]" if default else "[y/N]"
        value = input(f"{label} {suffix}: ").strip().lower()
        if not value:
            return default
        return value in {"y", "yes"}

    def choose_one(
        self,
        label: str,
        options: Sequence[T],
        render: Callable[[T], str],
    ) -> T:
        if not options:
            raise UserFacingError(f"No options available for {label}.")
        print(label)
        for index, option in enumerate(options, start=1):
            print(f"{index}. {render(option)}")
        raw_value = input("Choice: ").strip()
        if not raw_value:
            raise UserFacingError("A selection is required.")
        try:
            selected_index = int(raw_value)
        except ValueError as exc:  # pragma: no cover
            raise UserFacingError(f"Invalid selection: {raw_value}") from exc
        if selected_index < 1 or selected_index > len(options):
            raise UserFacingError(f"Selection out of range: {raw_value}")
        return options[selected_index - 1]
