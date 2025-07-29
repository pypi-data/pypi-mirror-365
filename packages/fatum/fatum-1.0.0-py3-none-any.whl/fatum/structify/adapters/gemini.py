from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Literal, overload

import instructor
from google import genai
from google.genai.types import GenerateContentConfig, GenerateContentResponse
from openai.types.chat import ChatCompletionMessageParam

from fatum.structify.adapters.base import BaseAdapter
from fatum.structify.config import GeminiProviderConfig
from fatum.structify.hooks import ahook_instructor
from fatum.structify.types import BaseModelT

if TYPE_CHECKING:
    from fatum.structify.config import CompletionResult, Message
    from fatum.structify.hooks import CompletionTrace


class GeminiAdapter(BaseAdapter[GeminiProviderConfig, genai.Client, GenerateContentResponse]):
    def _create_client(self) -> genai.Client:
        return genai.Client(api_key=self.provider_config.api_key)

    def _with_instructor(self) -> instructor.AsyncInstructor:
        client: genai.Client = self.client
        return instructor.from_genai(client, use_async=True, mode=self.instructor_config.mode)  # type: ignore[no-any-return]

    @overload
    async def acreate(
        self,
        messages: list[Message],
        response_model: type[BaseModelT],
        *,
        with_hooks: Literal[False] = False,
        **kwargs: Any,
    ) -> BaseModelT: ...

    @overload
    async def acreate(
        self,
        messages: list[Message],
        response_model: type[BaseModelT],
        *,
        with_hooks: Literal[True],
        **kwargs: Any,
    ) -> CompletionResult[BaseModelT, GenerateContentResponse]: ...

    async def acreate(
        self,
        messages: list[Message],
        response_model: type[BaseModelT],
        with_hooks: bool = False,
        **kwargs: Any,
    ) -> BaseModelT | CompletionResult[BaseModelT, GenerateContentResponse]:
        formatted_messages = self._format_messages(messages)
        model = self.completion_params.model
        config = GenerateContentConfig(**self.completion_params.model_dump(exclude={"model"}))
        captured: CompletionTrace[GenerateContentResponse]

        async with ahook_instructor(self.instructor, enable=with_hooks) as captured:
            response = await self.instructor.create(
                model=model,
                response_model=response_model,
                messages=formatted_messages,
                **self.instructor_config.model_dump(exclude={"mode"}),
                config=config,
                **kwargs,
            )
            return self._assemble(response, captured, with_hooks)

    async def _astream(
        self,
        formatted_messages: list[ChatCompletionMessageParam],
        response_model: type[BaseModelT],
        with_hooks: bool = False,
    ) -> AsyncIterator[BaseModelT | CompletionResult[BaseModelT, GenerateContentResponse]]:
        model = self.completion_params.model
        config = GenerateContentConfig(**self.completion_params.model_dump(exclude={"model"}))

        captured: CompletionTrace[GenerateContentResponse]
        async with ahook_instructor(self.instructor, enable=with_hooks) as captured:
            async for partial in self.instructor.create_partial(
                model=model,
                response_model=response_model,
                messages=formatted_messages,
                **self.instructor_config.model_dump(exclude={"mode"}),
                config=config,
            ):
                yield self._assemble(partial, captured, with_hooks)
