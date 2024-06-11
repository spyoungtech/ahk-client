import threading
from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

import requests
from ahk import AHK
from ahk import Control
from ahk import FutureResult
from ahk import Window
from ahk._sync.transport import Transport
from ahk._types import FunctionName
from ahk.directives import Directive
from ahk.extensions import _extension_registry
from ahk.extensions import _ExtensionMethodRegistry
from ahk.extensions import _resolve_extensions
from ahk.extensions import Extension
from ahk.message import RequestMessage
from ahk.message import ResponseMessage


class AHKClient(AHK):
    def __init__(self, host: str):
        extensions = None
        self._transport = HTTPTransport(host=host)
        self._version: Literal['v1', 'v2'] = self._transport.get_version()
        self._extension_registry: _ExtensionMethodRegistry
        self._extensions: list[Extension]
        self._version: Literal['v1', 'v2'] = self._version
        self._extension_registry: _ExtensionMethodRegistry
        self._extensions: list[Extension]
        if extensions == 'auto':
            self._extensions = [ext for ext in _extension_registry if ext._requires in (None, self._version)]
        else:
            self._extensions = _resolve_extensions(extensions) if extensions else []
            for ext in self._extensions:
                if ext._requires not in (None, self._version):
                    raise ValueError(
                        f'Incompatible extension detected. Extension requires AutoHotkey {ext._requires} but server version is {self._version}'
                    )
        self._method_registry = _ExtensionMethodRegistry(sync_methods={}, async_methods={})
        for ext in self._extensions:
            self._method_registry.merge(ext._extension_method_registry)


class HTTPTransport(Transport):
    def __init__(
        self,
        /,
        host: str,
        **kwargs: Any,
    ):
        self._host = host
        self._hotkey_transport = None
        self._directives: list[Union[Directive, Type[Directive]]] = []
        self._version: Optional[Literal['v1', 'v2']] = None
        self.lock = threading.Lock()

    def function_call(
        self,
        function_name: FunctionName,
        args: Optional[List[str]] = None,
        blocking: bool = True,
        engine: Optional[AHK[Any]] = None,
    ) -> Any:
        request = RequestMessage(function_name=function_name, args=args)
        if blocking:
            return self.send(request, engine=engine)
        else:
            return self.send_nonblocking(request, engine=engine)

    def get_version(self) -> Literal['v1', 'v2']:
        resp = requests.get(f'{self._host}/version')
        resp.raise_for_status()
        content = resp.json()
        return content['version']

    def run_script(
        self, script_text_or_path: str, /, *, blocking: bool = True, timeout: Optional[int] = None
    ) -> Union[str, FutureResult[str]]:
        raise NotImplementedError()

    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AHK[Any]] = None
    ) -> FutureResult[Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]]:
        raise NotImplementedError()

    def send(
        self, request: RequestMessage, engine: Optional[AHK[Any]] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]:
        with self.lock:
            response = requests.post(f'{self._host}/{request.function_name}', json=request.args)
        response.raise_for_status()
        content = response.content
        print(content)
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore
