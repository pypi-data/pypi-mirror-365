# chat-object

![doctest](https://img.shields.io/badge/doctest-90%25_coverage-green)
![license](https://img.shields.io/badge/license-MIT-lightblue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)

A simple library for creating and managing chat objects and messages for LLM applications.

## Installation

```bash
pip install chat-object
```

## Quick Start

```python
import openai
from chat_object import Chat, Message, Role

client = openai.OpenAI()

chat = Chat(
    Message(Role.System, "You are a helpful assistant"),
    Message(Role.User, "Hello!")
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=chat.as_dict()
)

print(response.choices[0].message.content)
```

> [!TIP]
> See [example_usage.py](example_usage.py) for more examples.

## Features

- **Well-tested code**: Comprehensive test coverage with doctests throughout the codebase
- **Type safety**: Full type hints and enum-based roles
- **Backward compatibility**: almost seamless integration with existing APIs
- **Immutable design**: Safe message handling with copy methods

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.