# Additional Gemini API Patterns

## Table of Contents
- [YouTube Processing](#youtube-processing)
- [Video Files](#video-files)
- [Audio Files](#audio-files)
- [PDF Files](#pdf-files)
- [Token Counting](#token-counting)
- [Error Handling](#error-handling)
- [Aspect Ratio Reference](#aspect-ratio-reference)
- [Thinking Budget (Legacy)](#thinking-budget-legacy)
- [Google Maps Grounding](#google-maps-grounding)

## YouTube Processing

```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=types.Content(
        parts=[
            types.Part(text="Summarize this video"),
            types.Part(
                file_data=types.FileData(
                    file_uri="https://www.youtube.com/watch?v=VIDEO_ID"
                )
            )
        ]
    )
)
```

**Note:** Only one YouTube link per request. Don't put URLs in text—use `file_data`.

## Video Files

```python
# Upload video
video_file = client.files.upload(file="video.mp4")
print(f"Uploaded: {video_file.uri}")

# Wait for processing
import time
while video_file.state == "PROCESSING":
    print("Processing...")
    time.sleep(10)
    video_file = client.files.get(name=video_file.name)

if video_file.state == "FAILED":
    raise ValueError("Video processing failed")

# Use video
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[video_file, "Describe what happens in this video"]
)
```

## Audio Files

```python
audio_file = client.files.upload(file="audio.mp3")

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        audio_file,
        "Transcribe and summarize this audio"
    ]
)
```

## PDF Files

```python
pdf_file = client.files.upload(file="document.pdf")

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[pdf_file, "Extract the key points as bullet points"]
)
```

## Token Counting

```python
# Count before sending
response = client.models.count_tokens(
    model="gemini-3-pro-preview",
    contents="Your prompt here"
)
print(f"Tokens: {response.total_tokens}")

# After generation, check usage
response = client.models.generate_content(...)
print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
print(f"Output tokens: {response.usage_metadata.candidates_token_count}")
print(f"Thinking tokens: {response.usage_metadata.thoughts_token_count}")
```

## Error Handling

```python
from google.genai import errors

try:
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents="..."
    )
except errors.ClientError as e:
    print(f"Client error: {e}")
except errors.ServerError as e:
    print(f"Server error (retry): {e}")

# Check for blocked content
if response.candidates[0].finish_reason == "SAFETY":
    print("Response blocked by safety filters")
    for rating in response.candidates[0].safety_ratings:
        print(f"  {rating.category}: {rating.probability}")
```

## Aspect Ratio Reference

### Image Output (Nano-Banana) - All 1290 tokens

| Ratio | Resolution |
|-------|------------|
| 1:1 | 1024x1024 |
| 2:3 | 832x1248 |
| 3:2 | 1248x832 |
| 3:4 | 864x1184 |
| 4:3 | 1184x864 |
| 9:16 | 768x1344 |
| 16:9 | 1344x768 |
| 21:9 | 1536x672 |

### Nano-Banana Pro - Higher Resolutions

| Ratio | 1K | 2K | 4K |
|-------|----|----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 4096x4096 |
| 16:9 | 1376x768 | 2752x1536 | 5504x3072 |
| 9:16 | 768x1376 | 1536x2752 | 3072x5504 |

4K images cost more tokens (2000 vs 1210).

### Imagen Aspect Ratios

`1:1`, `3:4`, `4:3`, `16:9`, `9:16`

## Thinking Budget (Legacy)

For Gemini 2.5 models (still supported on Gemini 3):

```python
# Disable thinking (Flash/Flash-Lite only)
config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

# Increase thinking (up to 24576)
config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_budget=8192
    )
)
```

**Gemini 3 Pro only supports** `thinking_level`: `"low"` or `"high"`.

## Google Maps Grounding

**Note:** Not supported on Gemini 3 models yet.

```python
# Works on Gemini 2.5 models
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Find coffee shops near here",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())],
        tool_config=types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(latitude=40.7680, longitude=-73.9819)
            )
        )
    )
)
```

## Per-File Media Resolution (Gemini 3)

Control resolution per file in the same request:

```python
# Requires v1alpha API version
client = genai.Client(
    api_key=API_KEY,
    http_options={"api_version": "v1alpha"}
)

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        types.Part(
            file_data=types.FileData(
                file_uri=uploaded_file.uri,
                mime_type=uploaded_file.mime_type
            ),
            media_resolution=types.PartMediaResolution(
                level="MEDIA_RESOLUTION_HIGH"
            )
        ),
        "Analyze this image"
    ]
)
```

## Batch Image Mixing

Nano-Banana Pro supports up to 14 images (6 high-fidelity):

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "Create a scene with all these characters",
        Image.open("char1.png"),
        Image.open("char2.png"),
        Image.open("char3.png"),
        Image.open("background.png"),
    ],
    config=types.GenerateContentConfig(
        response_modalities=["Image"]
    )
)
```

## Image Translation

```python
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=["Text", "Image"],
        tools=[{"google_search": {}}]
    )
)

# Create in one language
response = chat.send_message("Create an infographic about climate change in Spanish")

# Translate to another
response = chat.send_message("Translate to Japanese, keeping the same layout")
```
