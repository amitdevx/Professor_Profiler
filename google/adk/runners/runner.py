class Runner:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    class _Part:
        def __init__(self, text: str):
            self.text = text

    class _Content:
        def __init__(self, text: str):
            self.parts = [Runner._Part(text)]

    class _Event:
        def __init__(self, text: str):
            self.content = Runner._Content(text)

        def is_final_response(self):
            return True

    async def run_async(self, **kwargs):
        # Minimal stub: yield a single final response event that echoes the
        # user's new_message text if available, or a default message.
        text = "mock response"
        new_message = kwargs.get("new_message")
        try:
            # Attempt to extract text from provided genai types if present
            if new_message and hasattr(new_message, "parts") and len(new_message.parts) > 0:
                text = getattr(new_message.parts[0], "text", text)
        except Exception:
            pass

        yield Runner._Event(text)
