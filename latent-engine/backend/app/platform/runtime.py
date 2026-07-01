from __future__ import annotations

from dataclasses import dataclass

from app.platform.config import Configuration
from app.platform.config import ConfigurationProvider
from app.platform.di import ServiceCollection
from app.platform.event_bus import EventBus
from app.platform.health import HealthRegistry
from app.platform.lifecycle import LifecycleManager
from app.platform.module import ModuleRegistry
from app.platform.observability import AuditLog
from app.platform.observability import MetricsRecorder
from app.platform.observability import StructuredLogger
from app.platform.plugin import PluginRegistry
from app.platform.scheduler import Scheduler


@dataclass
class PlatformRuntime:
    modules: ModuleRegistry
    services: ServiceCollection
    event_bus: EventBus
    configuration: ConfigurationProvider
    scheduler: Scheduler
    plugins: PluginRegistry
    logger: StructuredLogger
    metrics: MetricsRecorder
    audit_log: AuditLog

    @classmethod
    def create(
        cls,
        configuration: Configuration | None = None,
    ) -> "PlatformRuntime":
        return cls(
            modules=ModuleRegistry(),
            services=ServiceCollection(),
            event_bus=EventBus(),
            configuration=ConfigurationProvider(
                configuration or Configuration()
            ),
            scheduler=Scheduler(),
            plugins=PluginRegistry(),
            logger=StructuredLogger(),
            metrics=MetricsRecorder(),
            audit_log=AuditLog(),
        )

    def register_module(
        self,
        module,
    ) -> None:
        self.modules.register(module)
        module.configure_services(self.services)
        self.audit_log.append(
            action="module_registered",
            actor="platform",
            target=module.name,
            metadata={
                "version": module.version,
                "capabilities": module.capabilities,
            },
        )

    def build(
        self,
    ) -> "BuiltPlatformRuntime":
        provider = self.services.build_provider()
        health = HealthRegistry(self.modules)
        lifecycle = LifecycleManager(self.modules)
        return BuiltPlatformRuntime(
            runtime=self,
            provider=provider,
            health=health,
            lifecycle=lifecycle,
        )


@dataclass
class BuiltPlatformRuntime:
    runtime: PlatformRuntime
    provider: object
    health: HealthRegistry
    lifecycle: LifecycleManager

    def initialize(
        self,
    ) -> None:
        self.lifecycle.initialize(self)

    def start(
        self,
    ) -> None:
        self.lifecycle.start()

    def shutdown(
        self,
    ) -> None:
        self.lifecycle.stop()
        self.lifecycle.shutdown()

