"""Command models to engage a user to empty a Flex Stacker."""

from __future__ import annotations
from typing import Optional, Literal, TYPE_CHECKING, Annotated
from typing_extensions import Type

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from ..command import AbstractCommandImpl, BaseCommand, BaseCommandCreate, SuccessData
from ...errors import (
    ErrorOccurrence,
)
from ...errors.exceptions import FlexStackerLabwarePoolNotYetDefinedError
from ...state import update_types
from ...types import StackerFillEmptyStrategy
from opentrons.calibration_storage.helpers import uri_from_details

if TYPE_CHECKING:
    from ...state.state import StateView
    from ...execution import RunControlHandler

FillCommandType = Literal["flexStacker/fill"]


class FillParams(BaseModel):
    """The parameters defining how a stacker should be filled."""

    moduleId: str = Field(..., description="Unique ID of the Flex Stacker")

    strategy: StackerFillEmptyStrategy = Field(
        ...,
        description=(
            "How to fill the stacker. "
            "If manualWithPause, pause the protocol until the client sends an interaction, and apply "
            "the new specified count thereafter. If logical, do not pause but immediately apply the "
            "specified count."
        ),
    )

    message: str | SkipJsonSchema[None] = Field(
        None,
        description="The message to display on connected clients during a manualWithPause strategy fill.",
    )

    count: Optional[Annotated[int, Field(ge=1)]] = Field(
        None,
        description=(
            "How full the labware pool should now be. If None, default to the maximum amount "
            "of the currently-configured labware the pool can hold. "
            "If this number is larger than the maximum the pool can hold, it will be clamped to "
            "the maximum. If this number is smaller than the current amount of labware the pool "
            "holds, it will be clamped to that minimum. Do not use the value in the parameters as "
            "an outside observer; instead, use the count value from the results."
        ),
    )


class FillResult(BaseModel):
    """Result data from a stacker fill command."""

    count: int = Field(
        ..., description="The new amount of labware stored in the stacker labware pool."
    )
    primaryLabwareURI: str = Field(
        ...,
        description="The labware definition URI of the primary labware.",
    )
    adapterLabwareURI: str | SkipJsonSchema[None] = Field(
        None,
        description="The labware definition URI of the adapter labware.",
    )
    lidLabwareURI: str | SkipJsonSchema[None] = Field(
        None,
        description="The labware definition URI of the lid labware.",
    )


class FillImpl(AbstractCommandImpl[FillParams, SuccessData[FillResult]]):
    """Implementation of a stacker fill command."""

    def __init__(
        self, state_view: StateView, run_control: RunControlHandler, **kwargs: object
    ) -> None:
        self._state_view = state_view
        self._run_control = run_control

    async def execute(self, params: FillParams) -> SuccessData[FillResult]:
        """Execute the stacker fill command."""
        stacker_state = self._state_view.modules.get_flex_stacker_substate(
            params.moduleId
        )

        if stacker_state.pool_primary_definition is None:
            location = self._state_view.modules.get_location(params.moduleId)
            raise FlexStackerLabwarePoolNotYetDefinedError(
                message=f"The Flex Stacker in {location} has not been configured yet and cannot be filled."
            )

        count = (
            params.count if params.count is not None else stacker_state.max_pool_count
        )
        new_count = min(
            stacker_state.max_pool_count, max(stacker_state.pool_count, count)
        )

        state_update = (
            update_types.StateUpdate().update_flex_stacker_labware_pool_count(
                params.moduleId, new_count
            )
        )

        if params.strategy == StackerFillEmptyStrategy.MANUAL_WITH_PAUSE:
            await self._run_control.wait_for_resume()

        if stacker_state.pool_primary_definition is None:
            raise FlexStackerLabwarePoolNotYetDefinedError(
                "The Primary Labware must be defined in the stacker pool."
            )

        return SuccessData(
            public=FillResult(
                count=new_count,
                primaryLabwareURI=uri_from_details(
                    stacker_state.pool_primary_definition.namespace,
                    stacker_state.pool_primary_definition.parameters.loadName,
                    stacker_state.pool_primary_definition.version,
                ),
                adapterLabwareURI=uri_from_details(
                    stacker_state.pool_adapter_definition.namespace,
                    stacker_state.pool_adapter_definition.parameters.loadName,
                    stacker_state.pool_adapter_definition.version,
                )
                if stacker_state.pool_adapter_definition is not None
                else None,
                lidLabwareURI=uri_from_details(
                    stacker_state.pool_lid_definition.namespace,
                    stacker_state.pool_lid_definition.parameters.loadName,
                    stacker_state.pool_lid_definition.version,
                )
                if stacker_state.pool_lid_definition is not None
                else None,
            ),
            state_update=state_update,
        )


class Fill(BaseCommand[FillParams, FillResult, ErrorOccurrence]):
    """A command to fill the Flex Stacker with labware."""

    commandType: FillCommandType = "flexStacker/fill"
    params: FillParams
    result: Optional[FillResult] = None

    _ImplementationCls: Type[FillImpl] = FillImpl


class FillCreate(BaseCommandCreate[FillParams]):
    """A request to execute a Flex Stacker fill command."""

    commandType: FillCommandType = "flexStacker/fill"
    params: FillParams

    _CommandCls: Type[Fill] = Fill
