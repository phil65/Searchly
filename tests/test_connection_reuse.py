"""Each anyenv-based provider reuses one connection for its searches."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import TYPE_CHECKING, Any

import anyenv
import pytest

from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient
from searchly.providers.jigsawstack_provider.jigsawstack import AsyncJigsawStackClient
from searchly.providers.kagi_provider.client import AsyncKagiClient
from searchly.providers.linkup_provider.client import AsyncLinkUpClient
from searchly.providers.search1_provider.client import AsyncSearch1API
from searchly.providers.serpapi_provider.client import AsyncSerpAPIClient
from searchly.providers.serper_provider.client import AsyncSerperClient
from searchly.providers.you_provider.you import AsyncYouClient


if TYPE_CHECKING:
    from collections.abc import Iterator


# Enough of every provider's response shape for an empty result.
BODY = json.dumps({
    "status_code": 20000,
    "tasks": [{"status_code": 20000, "result": None}],
    "results": [],
    "data": [],
}).encode()


class Server(ThreadingHTTPServer):
    daemon_threads = True
    connections = 0

    def process_request(self, request: Any, client_address: Any) -> None:
        self.connections += 1
        super().process_request(request, client_address)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # keep-alive

    def _reply(self) -> None:
        if length := int(self.headers.get("content-length") or 0):
            self.rfile.read(length)
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(BODY)))
        self.end_headers()
        self.wfile.write(BODY)

    do_GET = do_POST = _reply  # noqa: N815

    def log_message(self, *_: Any) -> None:
        pass


@pytest.fixture
def server() -> Iterator[Server]:
    server = Server(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def _providers(url: str) -> list[Any]:
    serpapi = AsyncSerpAPIClient(api_key="k")
    serpapi.BACKEND = url  # ty: ignore[invalid-assignment]
    return [
        AsyncDataForSEOClient(login="l", password="p", base_url=url),
        AsyncJigsawStackClient(api_key="k", base_url=url),
        AsyncKagiClient(api_key="k", base_url=url),
        AsyncLinkUpClient(api_key="k", base_url=url),
        AsyncSearch1API(api_key="k", base_url=url),
        serpapi,
        AsyncSerperClient(api_key="k", base_url=url),
        AsyncYouClient(api_key="k", base_url=url),
    ]


@pytest.mark.parametrize("index", range(8))
async def test_searches_share_one_connection(server: Server, index: int):
    url = f"http://127.0.0.1:{server.server_address[1]}"
    provider = _providers(url)[index]
    async with provider:
        for _ in range(3):
            await provider.web_search("query")
    assert server.connections == 1
    assert provider._http_session is None  # closed on exit


def test_a_new_event_loop_gets_a_new_session(server: Server):
    url = f"http://127.0.0.1:{server.server_address[1]}"
    provider = AsyncKagiClient(api_key="k", base_url=url)
    anyenv.run_sync(provider.web_search("a"))
    anyenv.run_sync(provider.web_search("b"))  # the first loop's client is unusable here
    assert server.connections == 2  # noqa: PLR2004
