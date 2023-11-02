# Settings
## Secrets
The file `./conifigs/secrets.yaml` contains your telegram bot and openai keys as well as other information.
```yaml
telegram_token: "TELEGRAM_BOT_TOKEN"
openai_token: "OPENAI_API_KEY"
restrictions_type: blacklist  # Use blacklist or whitelist type access restriction
mongodb_url: "mongodb://127.0.0.1:27017"  # Url to mongodb server
mongodb_name: "summary_bot"  # db name
settings_collection: "settings"  # collection names
tokens_collection: "tokens"
telegram_collection: "telegram"
admin_id: 123456789  # Your telegram id, provides you the special access to bot
```

## Bot settings
You can change bot's settings here, like choosing which model to use.

```yaml
text_model: 'synthia'  # Name of text model from ./configs/text_models.yaml
audio_model: 'whisper_local'  # Name of audio model from ./configs/text_models.yaml

max_tasks: 5  # Determines how many tasks you can queue
			  # The next task will result in error
return_type: doc  # How to show results, useful for debugging
				  # 'doc', 'print', 'answer'

```

## Database defaults
Providing default values for newly registered users

#### Settings defaults
```yaml
change_language: 'English'
document_format: 'markdown'
text_format: 'speech'
document_language: 'auto'
```

#### Token defaults

```yaml
current_tokens: 20000  # Grant this many tokens to users freely
```

#### Telegram defaults

```yaml
is_admin: False
```