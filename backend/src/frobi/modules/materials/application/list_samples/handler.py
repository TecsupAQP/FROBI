from frobi.modules.materials.application.ports import SampleCatalog
from frobi.modules.materials.domain import Material


class ListSamplesHandler:
    def __init__(self, samples: SampleCatalog) -> None:
        self._samples = samples

    async def handle(self) -> list[Material]:
        return self._samples.list()
