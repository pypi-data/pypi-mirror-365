# PromptStream SDK

A small client library for interacting with the PromptStream API.

## Usage

```python
from promptstream.client import PromptStreamClient

client = PromptStreamClient(api_key="your-key")

# run a prompt
resp = client.run_prompt("prompt-123", {"name": "Alice"})

# track different outcomes
client.track_click(resp.run_id, "prompt-123", "cta", source="app")
client.track_conversion(resp.run_id, "prompt-123", "signup", source="app")
client.track_feedback(resp.run_id, "prompt-123", "feedback", True, source="app")
client.track_rating(resp.run_id, "prompt-123", "rating", 5, source="app")
client.track_engagement(resp.run_id, "prompt-123", "scroll", 80, source="app")
```
