from __future__ import annotations

from collections.abc import Callable

from benchforge.models.base import ModelAdapter
from benchforge.models.mock import MockModelAdapter

AdapterFactory = Callable[..., ModelAdapter]

_REGISTRY: dict[str, AdapterFactory] = {
    "mock": MockModelAdapter,
}


def register(name: str, factory: AdapterFactory) -> None:
    _REGISTRY[name] = factory


def get_adapter(name: str, **kwargs: object) -> ModelAdapter:
    try:
        factory = _REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise KeyError(f"Unknown model adapter '{name}'. Registered: {known}") from exc
    return factory(**kwargs)  # type: ignore[arg-type]


def list_adapters() -> list[str]:
    return sorted(_REGISTRY)
