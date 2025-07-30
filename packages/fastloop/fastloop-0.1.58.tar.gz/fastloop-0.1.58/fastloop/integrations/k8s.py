from typing import TYPE_CHECKING

from ..integrations import Integration
from ..logging import setup_logger
from ..loop import LoopEvent
from ..types import IntegrationType, K8SConfig

if TYPE_CHECKING:
    from ..fastloop import FastLoop

logger = setup_logger(__name__)


class PodCreatedEvent(LoopEvent):
    type: str = "pod_created"
    pod_id: str


SUPPORTED_K8S_EVENTS = ["pod_created"]


class K8SIntegration(Integration):
    def __init__(
        self,
        *,
        api_server_url: str,
    ):
        super().__init__()

        self.config = K8SConfig(api_server_url=api_server_url)

    def type(self) -> IntegrationType:
        return IntegrationType.K8S

    def register(self, fastloop: "FastLoop", loop_name: str) -> None:
        fastloop.register_events(
            [
                PodCreatedEvent,
            ]
        )

        self._fastloop: FastLoop = fastloop
        # self._fastloop.app.add_api_route(
        #     path=f"/{loop_name}/k8s/events",
        #     endpoint=self._handle_slack_event,
        #     methods=["POST"],
        #     response_model=None,
        # )
        self.loop_name: str = loop_name
