# Configuring bot's responses

Here is the process of creating a new configuration file with bot's responses. You can use the template to make things easier for youself.
> The text structure should follow Markdown syntax.  
> To make a multiline answer, use symbol "`|`"

Firstly, Create YAML file in`./configs/bot_locale/` directory.

Let's configure some metadata:
```yaml
language: English
code: en
```
`language` - language name. It will be shown to user.   
`code` - language locale code. It is used to determine which language should be used for each user in default.  

### Configuring settings:

```yaml
start: 
  message: |
    welcome message
  description: Start bot

cancel:
  message: canceled
  description: Cancel current task
help:
  message: |
    help message
    sample text
  description: Displays help message
change_language: 
  message: |
    change bots language to
  description: Change bot's interface language
  button1: "English"
  button2: "русский"

```

The general structure is:  

```yaml
command:
  message: command message
  description: command description
  button1: param1
  value1: true_value1
  button2: param2
  value2: true_value2
  ...
  buttonN: paramN
  valueN: true_valueN
```  
`message` - Message which bot writes then configuring this setting.    
`description` - Command description in command list.  
`buttonN` - Shows button with this text.  
`valueN` - Send this string instead if user chooses this button.  

### `general` and `errors` tab
All keys in this section should exist in your config file. You can only change their values.  

Both tabs determine a message sent to user.
Example:  

```yaml

general:
  success: Success!
  got_link: Processing youtube video...
  got_video: Processing video...
  transcribing: Transcribing video, please wait...
  processing: Processing text, please wait...
  caption: Here is your document
  document_caption: Here is your summary!
  startup: Bot started
  shutdown: Bot shutdown

errors:
  critical: "Critical Error"
  bad_link: "Bad link"
  config_access: "Error: could not access config file with the provided keyword"
  composer: "Error in document generation"
  llm: "Error in text generation module"
  audio_model: "Error in transcription process"
  file_not_found: "Could not find file in the provided path"
  unknown_setting: "You chose a wrong setting, use keyboard next time or check configs"

```  
