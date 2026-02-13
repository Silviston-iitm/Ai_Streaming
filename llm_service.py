import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def stream_llm_response(prompt: str):
    """
    Streams response chunks from the LLM.
    Yields token chunks progressively.
    """

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an analyst. "
                        "Provide 9 key insights with evidence. "
                        "Write at least 900 characters."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta

            if delta and delta.content:
                yield delta.content

    except Exception as e:
        yield f"[ERROR] {str(e)}"
