# Chatbot Query Library
Python library for easy querying of popular chatbots, including Copilot, Gemini, GPT and Llama.

This library also has the ability to query multiple chatbots, with multiple prompts, multiple times, in parallel and save responses to a file.

> [!NOTE]
> This library is intended for educational and research purposes only. You should respect the terms of service of the chatbot providers.

This library was written as part of my master thesis, "Evaluating Biases in Conversational AI Systems" at the University of Zurich, and used in an upcoming publication. The source code is released under the MIT license.

## Chatbots
The following chatbot providers are supported:
 * Copilot
 * Gemini
 * Hugging Face (including Llama 2)
 * OpenAI (including GPT-3.5 and GPT-4)

There are some limitations to each provider:
 * Copilot: unofficial API, rate limited
 * Gemini: unofficial API, rate limited
 * Hugging Face: some models require a paid API key and/or model access requests, throttling may occur with free models
 * OpenAI: requires a paid API key

### Unofficial APIs
Due to the nature of querying chatbots with an unofficial API, this library may break if the chatbots update.

They are also subject to throttling and providers may block access if they detect excessive usage.

This library supports using multiple Microsoft and Google accounts to avoid per-account rate limiting.

## Installation
To install the library, ensure you have Python 3 and pip installed. Then, run the following command:

```bash
pip install https://github.com/jacobgelling/chatbot-query-library/archive/refs/tags/0.1.0.zip --upgrade
```

## Configuration
Before using the library, you need to configure the chatbot providers. This involves either setting an API key or creating browser sessions depending on the provider.

### Official APIs
Hugging Face and OpenAI require API keys to use their services.

The API keys can be obtained at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) respectively.

Llama 2 requires a paid Hugging Face API key to use, in addition to permission to access the model. Permission can be requested at [https://huggingface.co/meta-llama/Llama-2-7b-chat-hf](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf).

### Unofficial APIs
Copilot and Gemini both use unofficial APIs, so you need to provide browser profiles and Microsoft/Google accounts to use them.

By default the library uses the Edge web browser with all Edge profiles, except the default profile. You can customise this by passing a custom `CookieManager` object to unofficial API classes.

Edge profiles can be created by opening Edge, clicking on the profile icon, and then clicking "Setup new personal profile". You should then log into Copilot and Gemini using a Microsoft and Google account respectively in each Edge profile and use the chatbots in the browser to create a session that can be used by the library.
 
> [!WARNING]
> It's not recommended to use your personal Microsoft or Google account for this purpose, as it may be banned.

> [!TIP]
> Experience shows that at least 5 accounts in 5 Edge profiles are needed to avoid per-account rate limiting if running 24/7, though this is subject to change.

> [!TIP]
> You may have to run Edge from terminal with the optional argument ```--disable-features=LockProfileCookieDatabase``` to allow the library to access the cookies while the browser is running.

## Usage

### Simple Querying
The library provides a simple interface for querying popular chatbots. To do so, import the desired class from the `chatbot` module, then call the `query` method with a prompt to receive a response.

```python
import chatbot_query_library as cql

OPENAI_API_KEY = "XXXXXXXXXX"
HUGGING_FACE_API_KEY = "XXXXXXXXXX"

responses = {}

copilot = cql.chatbot.Copilot()
responses[copilot.name] = copilot.query("What's the best colour?")

gemini = cql.chatbot.Gemini()
responses[gemini.name] = gemini.query("What's the best colour?")

gpt35 = cql.chatbot.OpenAI(api_key=OPENAI_API_KEY)
responses[gpt35.name] = gpt35.query("What's the best colour?")

llama2 = cql.chatbot.HuggingFace(api_key=HUGGING_FACE_API_KEY)
responses[llama2.name] = llama2.query("What's the best colour?")

print(responses)
```

### Parallel Querying
The library also supports parallel querying of multiple chatbots. To use this feature, import the `MultiChatbot` class from the `multichatbot` module and create an instance with a list of chatbots and prompts, and number of runs. Then, call the `query` method with a prompt to receive responses from all chatbots.

```python
import chatbot_query_library as cql

OPENAI_API_KEY = "XXXXXXXXXX"
HUGGING_FACE_API_KEY = "XXXXXXXXXX"

copilot = cql.chatbot.Copilot()
gemini = cql.chatbot.Gemini()
gpt35 = cql.chatbot.OpenAI(api_key=OPENAI_API_KEY)
llama2 = cql.chatbot.HuggingFace(api_key=HUGGING_FACE_API_KEY)

chatbots = [copilot, gemini, gpt35, llama2]

prompts = ["What's the best colour?", "What's the best food?"]

multi_chatbot = cql.multichatbot.MultiChatbot(chatbots=chatbots, prompts=prompts, runs=2)
multi_chatbot.query()
```

During querying, logs and responses are saved to files by default in the `temp` directory. The filenames correspond to the chatbot names.

> [!TIP]
> If performing many queries with unofficial APIs, it's recommended to periodically check the logs in the `temp` directory to ensure the queries are running correctly. It's also recommended to periodically perform a query in the used browser profiles to refresh the session and complete any given captchas.

Once querying is complete, the files are combined into a single file by default in the `output` directory, with the following structure:

```json
[
    {
        "timestamp": 1704063600.0,
        "chatbot": "GPT-3.5",
        "prompt": "What's the best colour?",
        "temperature": 1.0,
        "response": "The best color is subjective and varies from person to person..."
    },
]
```

### Classes and Parameters

#### cql.chatbot
* Copilot
    * cookie_manager: CookieManager = CookieManager(domain_name="bing.com")
    * name: str = "Copilot"
    * timeout: int = 60
    * temperature: EdgeGPT.ConversationStyle = EdgeGPT.ConversationStyle.balanced
* Gemini
    * cookie_manager: CookieManager = CookieManager(domain_name="google.com")
    * name: str = "Gemini"
    * timeout: int = 60
* HuggingFace
    * api_key: str
    * name: str = "Llama 2"
    * model: str = "meta-llama/Llama-2-70b-chat-hf"
    * timeout: int = 60
    * temperature: float = 0.6
    * max_tokens: int = 2048
    * top_p: float = 0.9
    * top_k: int = 0
* OpenAI
    * api_key: str
    * name: str = "GPT-3.5"
    * model: str = "gpt-3.5-turbo"
    * timeout: int = 60
    * temperature: float = 1.0
    * max_tokens: int = 2048

#### cql.multichatbot
* MultiChatbot
    * chatbots: list
    * prompts: list
    * temp_dir: str = "temp"
    * output_dir: str = "output"
    * output_filename: str = "results.json"
    * runs: int = 1
    * max_errors: int = 5

#### cql.cookies
* CookieManager
    * domain_name: str = ""
    * prefix: str = None
    * browser: Callable = browser_cookie3.edge
    * cookie_files: list = None

#### cql.profiles
* ProfileGenerator
    * profiles: list = None
    * questions: list = None
