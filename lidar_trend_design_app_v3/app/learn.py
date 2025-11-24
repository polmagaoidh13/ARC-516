import json, os, time

class FeedbackStore:
    def __init__(self, path: str = "/tmp/feedback.jsonl"):
        self.path = path

    def record(self, purpose: str, style_prompt: str, liked: bool):
        with open(self.path, "a") as f:
            f.write(json.dumps({
                "ts": time.time(),
                "purpose": purpose,
                "style_prompt": style_prompt,
                "liked": liked
            }) + "\n")
