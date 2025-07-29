from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from fastapi.params import Depends as DependsT

from .chained_dependency_classes import (
    _ChainedDependencyAsyncGen,
    _ChainedDependencyCoroutine,
    _ChainedDependencyGen,
    _ChainedDependencySync,
)
from .utils import is_async_gen_callable, is_coroutine_callable, is_gen_callable

DependencyCallableT = Callable[..., Any]
HandlerT = DependencyCallableT | DependsT


class _DependsChainMeta(type):
    def __or__(cls, new_dependency: HandlerT) -> DependsChain:  # type: ignore[override]
        """Start a new chain with the given handler."""
        chain: DependsChain = cls()
        chain._add_link(new_dependency)
        return chain


class DependsChain(DependsT, metaclass=_DependsChainMeta):
    DEPENDS_CHAIN_INJECTED_PARAM_NAME = "_depends_chain_previous_dependency"

    def __init__(self) -> None:
        super().__init__()

    def _add_link(self, new_dependency: HandlerT) -> None:
        """Override current dependency and make it depend on the current one."""
        if isinstance(new_dependency, DependsT):
            new_callable = new_dependency.dependency
            new_use_cache = new_dependency.use_cache
        else:
            new_callable = new_dependency
            new_use_cache = True

        if self.dependency is None:
            self.dependency = new_callable
            self.use_cache = new_use_cache
            return

        current_dependency = Depends(self.dependency, use_cache=self.use_cache)

        if not callable(new_callable):
            raise TypeError(
                f"new_dependency must be a callable, got {type(new_callable)}.",
            )

        sig = inspect.signature(new_callable)
        params = list(sig.parameters.values())

        prev_param = inspect.Parameter(
            self.DEPENDS_CHAIN_INJECTED_PARAM_NAME,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[Any, current_dependency],
        )
        params.insert(0, prev_param)

        chained_dependency: Callable

        if is_async_gen_callable(new_callable):
            chained_dependency = _ChainedDependencyAsyncGen(
                new_callable,
                self.DEPENDS_CHAIN_INJECTED_PARAM_NAME,
                inspect.Signature(parameters=params, return_annotation=sig.return_annotation),
            )
        elif is_gen_callable(new_callable):
            chained_dependency = _ChainedDependencyGen(
                new_callable,
                self.DEPENDS_CHAIN_INJECTED_PARAM_NAME,
                inspect.Signature(parameters=params, return_annotation=sig.return_annotation),
            )
        elif is_coroutine_callable(new_callable):
            chained_dependency = _ChainedDependencyCoroutine(
                new_callable,
                self.DEPENDS_CHAIN_INJECTED_PARAM_NAME,
                inspect.Signature(parameters=params, return_annotation=sig.return_annotation),
            )
        elif callable(new_callable):
            chained_dependency = _ChainedDependencySync(
                new_callable,
                self.DEPENDS_CHAIN_INJECTED_PARAM_NAME,
                inspect.Signature(parameters=params, return_annotation=sig.return_annotation),
            )
        else:
            raise TypeError(f"Unsupported callable type: {type(new_callable)}")

        self.dependency = chained_dependency
        self.use_cache = new_use_cache

    def __or__(self, new_dependency: HandlerT) -> DependsChain:
        """Add a handler to the chain using the `|` operator."""
        self._add_link(new_dependency)
        return self
