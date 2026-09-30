from typing import Protocol

class Service(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...

class JROCRuntime:
    def __init__(self):
        self.services: dict[str, Service] = {}
        self.started = False

    def register_service(self, name: str, service: Service) -> None:
        self.services[name] = service

    async def start(self) -> None:
        for service in self.services.values():
            await service.start()
        self.started = True

    async def stop(self) -> None:
        for service in reversed(list(self.services.values())):
            await service.stop()
        self.started = False
