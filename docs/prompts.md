# Prompts
Prompts are passed to text models to act as a guidance for them. You can ask to use different writing styles, constrain output to a few sentences or write answer in a different language.

Files with prompts are located in `./configs/prompts/` 

The general prompt structure is
```yaml
{system}
Type which style do you want to use. How many sentences to output and so on. 
{instruction}
Write your precise instructions here{misc}:
{text}

{response}

```
`{system}`, `{instruction}`, `{response}` - are placeholders for special instruction which tell the model there your instructions start and end.  
`{text}` - The text to process will be placed here.  
`{misc}` - Other instructions, like which language to use.  

Every placeholder is necessary here.

### Combining prompts into map-reduce procedure

Let's use prompts to make a text summary.  

To make a new style, follow this structure:  
`./configs/prompts.yaml`.  
```yaml
summary_style:
  premap_name: str or list[str] # Names of premap tasks
  premap: str or list[str]  # Paths to premap txt files
  map: str  # Path to map txt file
  postmap_name: str or list[str]  # Names of postmap tasks
  postmap: str or list[str]  # Paths to postmap txt files
  reduce: str  # Path to reduce task
```

Map-reduce task divides text into a different smaller chunks using `map` prompts and then combines them using `reduce` prompt.  
There are also `premap` and `postmap` prompts, which can be used to better manipulate created text summary.  
> Their functions are:  
> `premap` - Transforms raw chunk of text and passes it to the output  
> `map` - Preprocess step before providing text to reduce task  
> `premap` - Transforms every chunk of mapped text before outputting it  
> `reduce` - Returns a single text string based on map outputs  

Diagram:  
![diagram][map-reduce-diagram]  

For example, you can use premap task to citate original text, map - to summarize each chapter, postmap - name each chapter and reduce - to make introduction.


[map-reduce-diagram]: ../assets/map_reduce_diagram.png