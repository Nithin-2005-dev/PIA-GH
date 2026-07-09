
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.platform.api.contracts import RuntimePipelineInput
from app.adapters.github.source import OfflineSnapshotSource
from app.adapters.github.adapter import GitHubAdapter
import app.platform.core_modules
class MockFactory:
    def create(self, token): return GitHubAdapter(source=OfflineSnapshotSource("evaluation/datasets/v1/facebook_react"))
app.platform.core_modules.GitHubAdapterFactory = MockFactory
from app.platform.runtime import PlatformRuntime
platform = PlatformRuntime.create()
r = platform.run(repository="facebook/react", commits=100)
print("Errors:", r.errors)
print("org_intelligence:", getattr(r.context, "org_intelligence", None) is not None)
print("forecast_context:", getattr(r.context, "forecast_context", None) is not None)
print("causal_context:", getattr(r.context, "causal_context", None) is not None)

