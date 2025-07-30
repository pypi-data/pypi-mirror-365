import logging
import typing
from abc import ABCMeta, abstractmethod

from unitelabs.cdk import sila

from .types.sila_types import HandoverPosition, InvalidCommandSequence, PositionIndex

logger = logging.getLogger(__name__)


class LabwareTransferSiteControllerBase(sila.Feature, metaclass=ABCMeta):
    """
    This feature (together with the "Labware Transfer Manipulator Controller" feature) provides commands to trigger the
    sub-tasks of handing over a labware item, e.g. a microtiter plate or a tube, from one device to another in a
    standardized and generic way.

    For each labware transfer a defined sequence of commands has to be called on both involved devices to ensure the
    proper synchronization of all necessary transfer actions without unwanted physical interferences and to optimize
    the transfer performance regarding the execution time. Using the generic commands, labware transfers between any
    arbitrary labware handling devices can be controlled (a robot device has not necessarily to be involved).

    Generally, a labware transfer is executed between a source and a destination device, where one of them is the
    active device (executing the handover actions) and the other one is the passive device.

    The "Labware Transfer Site Controller" feature is used to control the labware transfer on the side of the
    passive device to hand over labware to or take over labware from an active device, which provides the
    "Labware Transfer Manipulator Controller" feature.

    If a device is capable to act either as the active or as the passive device of a labware transfer it must provide
    both features.

    The complete sequence of issued transfer commands on both devices is as follows:

    1. Prior to the actual labware transfer a "Prepare For Output" command is sent to the source device to execute all
       necessary actions to be ready to release a labware item (e.g. open a tray) and simultaneously a "Prepare For
       Input" command is sent to the destination device to execute all necessary actions to be ready to receive a
       labware item (e.g. position the robotic arm near the tray of the source device).
    2. When both devices have successfully finished their "Prepare For ..." command execution, the next commands are
       issued.
    3a If the source device is the active device it will receive a "Put Labware" command to execute all necessary
       actions to put the labware item into the destination device. After the transfer has been finished successfully,
       the destination device receives a "Labware Delivered" command, that triggers all actions to be done after the
       labware item has been transferred (e.g. close the opened tray).
    3b If the destination device is the active device it will receive a "Get Labware" command to execute all necessary
       actions to get the labware from the source device (e.g. gripping the labware item). After that command has been
       finished successfully, the source device receives a "Labware Removed" command, that triggers all actions to be
       done after the labware item has been transferred (e.g. close the opened tray).

    The command sequences for a passive source or destination device have always to be as follows:
    - for a passive source device:        PrepareForOutput - LabwareRemoved
    - for a passive destination device:   PrepareForInput - LabwareDelivered

    If the commands issued by the client differ from the respective command sequences an "Invalid Command Sequence"
    error will be raised.

    To address the location, where a labware item can be handed over to or from other devices, every device must
    provide one or more uniquely named positions (handover positions) via the "Available Handover Positions" property.
    A robot (active device) should have at least one handover position for each device that it interacts with, whereas
    most passive devices will only have one handover position. In the case of a position array (e.g. a rack), the
    position within the array is specified via the sub-position of the handover position, passed as an index number.

    To address the positions within a device where the transferred labware item has to be stored at or is to be taken
    from (e.g. the storage positions inside an incubator), the internal position is specified. Each device must provide
    the number of available internal positions via the "Number Of Internal Positions" property. In the case of no
    multiple internal positions, this property as well as the "Internal Position" parameter value must be 1.

    With the "Prepare For Input" command there is also information about the labware transferred, like labware type or
    a unique labware identifier (e.g. a barcode).
    """

    @abstractmethod
    @sila.ObservableCommand(name="Prepare For Input", errors=[InvalidCommandSequence])
    async def PrepareForInput(
        self,
        HandoverPosition: HandoverPosition,
        InternalPosition: PositionIndex,
        LabwareType: str,
        LabwareUniqueID: str,
        *,
        status: sila.Status,
    ) -> None:
        """
        Put the device into a state in which it is ready to accept new labware at the specified handover position.

        .. parameter:: Indicates the position where the labware will be handed over.
        .. parameter:: Indicates the position which the labware will be stored at within the device, e.g. internal
                       storage positions of an incubator.
        .. parameter:: Specifies the type of labware that will be handed over to transfer information about the
                       labware that the device might need to handle it correctly.
        .. parameter:: Represents the unique identification of a labware in the controlling system. It is assigned
                       by the system and must remain unchanged during the whole process.
        """

    @sila.ObservableCommand(name="Prepare For Output", errors=[InvalidCommandSequence])
    async def PrepareForOutput(
        self,
        HandoverPosition: HandoverPosition,
        InternalPosition: PositionIndex,
        *,
        status: sila.Status,
    ) -> None:
        """
        Put the device into a state in which it is ready to release the labware at the specified handover position.

        .. parameter:: Indicates the position where the labware will be handed over.
        .. parameter:: Indicates the position which the labware will be retrieved from within the device, e.g. internal \
              storage positions of an incubator.

        """

    @abstractmethod
    @sila.ObservableCommand(name="Labware Delivered", errors=[InvalidCommandSequence])
    async def LabwareDelivered(
        self,
        HandoverPosition: HandoverPosition,
        *,
        status: sila.Status,
    ):
        """
        Notifies the passive destination device of a labware item that has been transferred to it (sent after a "Prepare \
              For Input" command)

        .. parameter:: Indicates the position the labware item has been delivered to.
        """

    @abstractmethod
    @sila.ObservableCommand(name="Labware Removed", errors=[InvalidCommandSequence])
    async def LabwareRemoved(
        self,
        HandoverPosition: HandoverPosition,
        *,
        status: sila.Status,
    ):
        """
        Notifies the passive source device of a labware item that has been removed from it (sent after a "Prepare For \
              Output" command).

        .. parameter:: Indicates the position the labware has been removed from.
        """

    @abstractmethod
    @sila.UnobservableProperty(name="Available Handover Positions")
    async def AvailableHandoverPositions(self) -> typing.List[HandoverPosition]:
        """
        All handover positions of the device including the number of sub-positions.
        """

    @sila.UnobservableProperty(name="Number Of Internal Positions")
    async def NumberOfInternalPositions(
        self,
    ) -> typing.Annotated[int, sila.constraints.MinimalInclusive(1)]:
        """
        The number of internal positions the device has.
        """
        return 1  # Default (not used)
