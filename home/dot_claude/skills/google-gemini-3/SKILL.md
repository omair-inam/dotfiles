---
name: google-gemini-3
description: Expert guidance for writing Python code using the Google Gemini API (google-genai SDK). Use this skill when writing code that calls Gemini models for text generation, multimodal prompts, image generation/editing (Nano-Banana models), embeddings, thinking configuration, file uploads, streaming, structured output (JSON), function calling, Google Search grounding, URL context, code execution, or context caching. Covers both Developer API and Vertex AI authentication patterns.
---

# Google Gemini 3 API

Expert patterns for the `google-genai` Python SDK. **Always prefer Gemini 3 models** over older generations.

## Model Selection

| Use Case | Model ID | Notes |
|----------|----------|-------|
| **Text Generation** | `gemini-3-pro-preview` | Best quality, thinking model |
| **Text (fast/cheap)** | `gemini-3-flash-preview` | Good balance |
| **Image Output** | `gemini-3-pro-image-preview` | Thinking + search, up to 4K |
| **Image (fast)** | `gemini-2.5-flash-image` | Cheaper, up to 1K |
| **Text-to-Image** | `imagen-4.0-generate-001` | Imagen family |
| **Embeddings** | `gemini-embedding-001` | 3072 dimensions |

## Client Initialization

### Developer API
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)
```

### Vertex AI
```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="global"  # Required for Gemini 3 preview models
)
```

## Text Generation

### Basic
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Your prompt here"
)
print(response.text)
```

### With System Instructions
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Your prompt",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant.",
        temperature=1.0,  # Recommended for Gemini 3
    )
)
```

### With Thinking (Gemini 3)
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Complex reasoning task",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="high",  # "minimal", "low", "medium", "high"
            include_thoughts=True   # To see thought process
        )
    )
)

for part in response.parts:
    if part.thought:
        print("Thought:", part.text)
    else:
        print("Answer:", part.text)
```

### Streaming
```python
for chunk in client.models.generate_content_stream(
    model="gemini-3-pro-preview",
    contents="Tell me a story"
):
    print(chunk.text, end="")
```

### Async
```python
response = await client.aio.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Your prompt"
)
```

## Multimodal Input

### Local Image (PIL)
```python
from PIL import Image

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        "Describe this image",
        Image.open("photo.jpg")
    ]
)
```

### GCS Image (Vertex AI)
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        types.Part.from_uri(
            file_uri="gs://bucket/image.jpg",
            mime_type="image/jpeg"
        ),
        "Describe this image"
    ]
)
```

### File Upload (large files, reuse)
```python
file_upload = client.files.upload(file="document.pdf")
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[file_upload, "Summarize this document"]
)
```

### Media Resolution Control
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[file_upload, "Analyze in detail"],
    config=types.GenerateContentConfig(
        media_resolution="MEDIA_RESOLUTION_HIGH"  # LOW, MEDIUM, HIGH
    )
)
```

## Image Generation (Nano-Banana)

### Generate Image
```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A cat wearing a space helmet",
    config=types.GenerateContentConfig(
        response_modalities=["Text", "Image"],  # or ["Image"] only
        image_config=types.ImageConfig(
            aspect_ratio="16:9",  # 1:1, 3:4, 4:3, 9:16, 16:9, etc.
            image_size="2K"       # 1K, 2K, 4K (Pro only)
        )
    )
)

for part in response.parts:
    if part.text:
        print(part.text)
    elif image := part.as_image():
        image.save("output.png")
```

### Edit Image (character consistency)
```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "Put this character on a beach",
        Image.open("character.png")
    ],
    config=types.GenerateContentConfig(
        response_modalities=["Image"]
    )
)
```

### Chat Mode (iterative editing)
```python
chat = client.chats.create(model="gemini-3-pro-image-preview")
response = chat.send_message("Create a toy fox figurine")
# ... later
response = chat.send_message("Add a hat to it")
```

## Image Generation (Imagen)

```python
result = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt="A serene mountain landscape at sunset",
    config=dict(
        number_of_images=2,
        aspect_ratio="16:9",
        person_generation="ALLOW_ADULT",
        output_mime_type="image/jpeg"
    )
)

for generated in result.generated_images:
    generated.image.show()
```

## Structured Output (JSON)

```python
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Give me a pancake recipe",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Recipe
    )
)

recipe = Recipe.model_validate_json(response.text)
```

## Tools & Grounding

### Google Search
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="What happened in the news today?",
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}]
    )
)
# Display grounding sources
print(response.candidates[0].grounding_metadata.web_search_queries)
```

### URL Context
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Compare these two recipes",
    config=types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext)]
    )
)
```

### Function Calling
```python
get_weather = types.FunctionDeclaration(
    name="get_weather",
    description="Get weather for a location",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING", "description": "City name"}
        },
        "required": ["location"]
    }
)

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="What's the weather in Paris?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=[get_weather])]
    )
)

# Check for function call
fc = response.candidates[0].content.parts[0].function_call
print(fc.name, fc.args)
```

### Code Execution
```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Calculate the 50th fibonacci number",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution)]
    )
)
```

## Embeddings

```python
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["First text", "Second text"],
    config=types.EmbedContentConfig(
        output_dimensionality=768  # Optional: reduce from 3072
    )
)

for emb in response.embeddings:
    print(len(emb.values))  # 768 or 3072
```

## Context Caching

```python
# Create cache (for repeated use of large context)
cached = client.caches.create(
    model="gemini-3-pro-preview",
    config=types.CreateCachedContentConfig(
        display_name="my-docs",
        system_instruction="You are a researcher",
        contents=[uploaded_file1, uploaded_file2],
        ttl="3600s"
    )
)

# Use cache
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Summarize the key findings",
    config=types.GenerateContentConfig(cached_content=cached.name)
)

# Delete when done
client.caches.delete(name=cached.name)
```

## Safety Settings

For creative/art applications that need relaxed filtering:

```python
SAFETY_OFF = [
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="...",
    config=types.GenerateContentConfig(safety_settings=SAFETY_OFF)
)
```

## Multi-turn Chat

```python
chat = client.chats.create(
    model="gemini-3-pro-preview",
    config=types.GenerateContentConfig(
        system_instruction="You are a coding assistant"
    )
)

response = chat.send_message("Write a fibonacci function")
response = chat.send_message("Now add memoization")

# Save/restore history
from pydantic import TypeAdapter
adapter = TypeAdapter(list[types.Content])
json_history = adapter.dump_json(chat.get_history())
# ... later
history = adapter.validate_json(json_history)
new_chat = client.chats.create(model="gemini-3-pro-preview", history=history)
```

## Quick Reference

See [references/patterns.md](references/patterns.md) for additional patterns:
- YouTube video processing
- PDF/Audio/Video file handling
- Token counting
- Error handling
