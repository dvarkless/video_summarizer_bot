# Configuring models

## Text models
There are two available LLM backends:
- OpenAI
- LlamaCpp

Configurations go into `./configs/models_text.yaml`
The general model config:

```yaml
model_name:
	name: name  # Model name, visual only
	provider: ProviderClass  # Class used to initiate the model
 	window_len: int  # Number or characters to feed into the model
	window_overlap: int # Number of overlapping characters 
						# Usually 5-10% from window_len
 	instruction_template: str  # Use the default for your model 
	system_template: str  # Use the default for your model
	response_template: str  # Use the default for your model
	available_context: int  # Maximum contex window in tokens
	model_params:  # Additional params to pass into the ProviderClass
		param1: val
		# ...
```

> Instruction, system, response template are usually provided in model readme. They are not necessary for OpenAI models, so leave them empty while using one.

`window_len` parameter is defined in characters, but it should not exceed the `available_context` defined in tokens. In English, 1 token ~= 0.8 words.   
Available providers are: `OpenAI`, `LlamaCpp`  
For more info about them checkout the [langchain docs](https://python.langchain.com/docs/modules/model_io/models/llms/)

There is the template chatGPT configuration:

```yaml
chatgpt:
  name: "gpt3.5-turbo"
  provider: OpenAI
  window_len: 5000  # Experiment with it
  window_overlap: 400
  instruction_template: ""  # Leave empty for chatgpt
  system_template: ""  # Leave empty for chatgpt
  response_template: ""  # Leave empty for chatgpt
  available_context: 4096
  model_params:
    model_name: "gpt3.5-turbo"
    temperature: 0.2  # How original the generated text should be
    					# 0.0 - stay strictly on topic
    					# 1.0 - default
    max_tokens: 512  # Maximum ammount of tokens to generate per 1 call

```

Using OpenAI models requires providing `OPENAI_API_KEY`  
Here is the example config for llamacpp model:

```yaml

synthia:
  name: "Synthia_13B_instruct"
  window_len: 5000
  window_overlap: 400
  instruction_template: "USER:"
  system_template: "SYSTEM:"
  response_template: "ASSISTANT:"
  provider: LlamaCpp
  available_context: 4096
  model_params:
    model_path: "path/to/your/model/model.gguf"
    
    # Genaration parameters
    temperature: 0.2
    top_p: 0.95
    repeat_penalty: 1.15
    top_k: 40
    f16_kv: True

    max_tokens: 400

	# Calculate parameters for your GPU
	# This config works for 12G Nvidia card
    n_gpu_layers: 42
    n_batch: 256
    n_ctx: 3500

	# Misc
    verbose: True

```

## Audio models

There are two available options:  
`WhisperLocal`, `WhisperCloud`

`WhisperLocal` uses either `openai-whisper` or `faster-whisper` libraries to transcribe videos on GPU or CPU. It downloads whisper models automatically into `./models/` directory.

`WhispersCloud` does computations on OpenAI servers and requires `OPENAI_API_KEY`  

Default configurations:  
```yaml
whisper_local:
  provider: WhisperLocal
  model_params:
    model_name: "large-v2"
    model_dir: "./models/whisper/"
    is_translate: False
    device: "cuda"

whisper_cloud:
  provider: WhisperCloud
  model_params:
    model_name: "whisper-1"
    model_dir: "./models/openai-whisper/"
    is_translate: False

```


## Embeddings

Embeddings are used to generate tokens from text. Tokens represent words as vectors, which can show similar or opposite words by meaning. It can be used to compress text without losing much data. In the bot, it happens then the input text exceeds 10 `window_len` number of characters.

In fact, embedding models are usually the same as text models. But you can use different embedding and text models.  
Available providers:  
`OpenAIEmbeddings`, `LlamaCppEmbeddings`, ...

Template config:

```yaml

chatgpt:
  provider: OpenAIEmbeddings
  available_context: 4096
  model_params:
    embedding_ctx_length: 4096

synthia:
  provider: LlamaCppEmbeddings
  available_context: 4096
  model_params:
    model_path: "path/to/model/model.gguf"
    n_ctx: 4096
    f16_kv: True

    n_gpu_layers: 0
    n_batch: 256

```