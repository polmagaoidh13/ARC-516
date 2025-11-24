import feedparser
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os, time, json, re
from typing import List

RSS = [
    "https://www.archdaily.com/feed",
    "https://www.dezeen.com/feed",
    "https://design-milk.com/feed/",
    "https://www.houseandgarden.co.uk/room/rss"
]

CATEGORIES = {
    "living room": ["sofa", "coffee table", "soft lighting", "natural textures"],
    "bedroom": ["soft textiles", "calming palette", "integrated storage"],
    "kitchen": ["durable surfaces", "efficient layout", "modular units"],
    "bathroom": ["moisture resistant finishes", "clean lines"]
}

TOK_WEIGHTS_DEFAULT = {
    "natural": 1.0, "timber": 1.0, "stone": 1.0, "modular": 1.0, "circular": 1.0, "neutral": 1.0, "warm": 1.0,
    "biophilic": 1.0, "textured": 1.0, "minimal": 1.0, "scandinavian": 1.0, "japandi": 1.0
}

class TrendEngine:
    def __init__(self, cache_path: str = "/tmp/trends.json", weights_path: str = "/tmp/style_weights.json"):
        self.cache_path = cache_path
        self.weights_path = weights_path
        self.model = None
        self._load_cache()
        self._load_weights()

    def _load_cache(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                self.cache = json.load(f)
        else:
            self.cache = {"styles": []}

    def _save_cache(self):
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)

    def _load_weights(self):
        if os.path.exists(self.weights_path):
            with open(self.weights_path, "r") as f:
                self.weights = json.load(f)
        else:
            self.weights = {"global": TOK_WEIGHTS_DEFAULT.copy(), "by_purpose": {}}

    def _save_weights(self):
        with open(self.weights_path, "w") as f:
            json.dump(self.weights, f)

    def refresh(self, limit: int = 100):
        items = []
        for url in RSS:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:limit]:
                    items.append(e.title)
            except Exception:
                continue
        # simple clean
        items = [re.sub(r"[^a-zA-Z0-9\s]", "", t).lower() for t in items]
        self.cache["styles"] = list(dict.fromkeys(items))[:400]
        self._save_cache()

    def _keywordize(self, text: str) -> List[str]:
        toks = re.findall(r"[a-zA-Z]+", text.lower())
        return [t for t in toks if len(t) > 2]

    def learn_from_feedback(self, purpose: str, style_prompt: str, liked: bool):
        delta = 0.2 if liked else -0.1
        toks = self._keywordize(style_prompt)
        for t in toks:
            self.weights["global"][t] = max(0.1, self.weights["global"].get(t, 1.0) + delta)
        bp = self.weights["by_purpose"].setdefault(purpose, {})
        for t in toks:
            bp[t] = max(0.1, bp.get(t, 1.0) + delta)
        self._save_weights()

    def get_style_prompt(self, purpose: str) -> str:
        if not self.cache.get("styles"):
            self.refresh()
        base = CATEGORIES.get(purpose.lower().strip(), ["contemporary"])
        recent = ", ".join(self.cache["styles"][:8])
        # weight boost words by learned weights
        def score_word(w):
            g = self.weights["global"].get(w, 1.0)
            p = self.weights["by_purpose"].get(purpose, {}).get(w, 1.0)
            return 0.6*g + 0.4*p
        # choose top weighted tokens from recent titles
        toks = []
        for t in self.cache["styles"][:50]:
            toks += self._keywordize(t)
        toks = list(dict.fromkeys(toks))
        toks.sort(key=score_word, reverse=True)
        chosen = ", ".join(toks[:6])
        prompt = f"{purpose} styled interior, {', '.join(base)}, current cues {chosen}"
        return prompt
