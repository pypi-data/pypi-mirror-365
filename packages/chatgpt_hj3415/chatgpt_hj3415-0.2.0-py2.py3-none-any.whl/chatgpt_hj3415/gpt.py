from openai import OpenAI
from typing import Iterator, Callable

'''def call_stream(messages: list[dict], temperature=0.7, response_format="text") -> Iterator[str]:
    """
    chunk 하나를 GPT에 보내고 생성되는 토큰을 delta 단위로 yield.
    마지막 yield 후 StopIteration.value 로 full_answer 반환.
    """
    client = OpenAI()

    full = ""
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        stream=True,
        # response_format={"type": "json_object"},
        response_format={"type": response_format},
    )

    for piece in stream:
        delta = piece.choices[0].delta.content
        if delta:
            full += delta
            yield delta  # <─ 여기서 즉시 전달

        if piece.choices[0].finish_reason and piece.choices[0].finish_reason != "length":
            break

    return full  # StopIteration.value'''


def call_stream(
    messages: list[dict],
    temperature: float = 0.7,
    response_format: str | None = None,   # "json_object" | None
    on_delta: Callable[[str], None] | None = None,
) -> str:
    """
    스트리밍으로 토큰을 on_delta 콜백에 전달하고,
    완료 후 전체 문자열을 반환합니다.
    """
    client = OpenAI()
    full = ""

    params = dict(model="gpt-4o", messages=messages, temperature=temperature, stream=True)
    if response_format == "json_object":
        params["response_format"] = {"type": "json_object"}  # 필요할 때만 설정

    stream = client.chat.completions.create(**params)

    for piece in stream:
        delta = piece.choices[0].delta.content
        if delta:
            full += delta
            if on_delta:
                on_delta(delta)

        fr = piece.choices[0].finish_reason
        if fr and fr != "length":
            break

    return full
