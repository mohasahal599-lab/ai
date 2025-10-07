import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import threading

# ---------------------------
# AgentRouter Client
# ---------------------------
class AgentRouterClaudeClient:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }

    def complete(self, prompt, model="claude-3-opus-20240229", max_tokens=512):
        url = f"{self.base_url}/v1/complete"
        body = {
            "model": model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens
        }

        resp = requests.post(url, headers=self._headers(), json=body)
        resp.raise_for_status()
        return resp.json()


# ---------------------------
# GUI Class
# ---------------------------
class ChatbotGUI:
    def __init__(self, root, client):
        self.client = client

        root.title("AgentRouter Claude Chatbot")
        root.geometry("600x600")

        # Chat history area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Input area
        self.entry = tk.Entry(root, font=("Arial", 12))
        self.entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

    def display_message(self, sender, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self, event=None):
        user_message = self.entry.get().strip()
        if not user_message:
            return

        self.display_message("You", user_message)
        self.entry.delete(0, tk.END)

        # Handle response in background thread
        threading.Thread(target=self.get_response, args=(user_message,)).start()

    def get_response(self, prompt):
        try:
            response = self.client.complete(prompt)
            text = response.get("completion", "").strip()
            if not text:
                text = json.dumps(response, indent=2)
        except Exception as e:
            text = f"[Error] {str(e)}"

        self.display_message("Claude", text)


# ---------------------------
# Main entry
# ---------------------------
if __name__ == "__main__":
    # Qabo config-ka
    BASE_URL = "https://agentrouter.org"
    AUTH_TOKEN = "sk-n71Svg1AIWKzgOzWVWHHUjF5NgI2gSlF5ujvQdzkfZvVriwv"  # <-- geli token-kaaga halkan

    client = AgentRouterClaudeClient(BASE_URL, AUTH_TOKEN)

    root = tk.Tk()
    gui = ChatbotGUI(root, client)
    root.mainloop()
