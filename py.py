import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import requests
import json
import threading
import os
from datetime import datetime
import webbrowser

# ---------------------------
# Configuration Management
# ---------------------------
class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "base_url": "https://agentrouter.org",
            "auth_token": "",
            "model": "claude-3-opus-20240229",
            "max_tokens": 1000,
            "theme": "dark"
        }
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.config = {**self.default_config, **config}
            else:
                self.config = self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

# ---------------------------
# AgentRouter Client
# ---------------------------
class AgentRouterClaudeClient:
    def __init__(self, config_manager):
        self.config = config_manager
        self.base_url = self.config.get("base_url").rstrip('/')
        self.auth_token = self.config.get("auth_token")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }

    def complete(self, prompt, model=None, max_tokens=None):
        if not self.auth_token:
            raise Exception("No authentication token provided. Please configure your API settings.")
        
        model = model or self.config.get("model")
        max_tokens = max_tokens or self.config.get("max_tokens")
        
        url = f"{self.base_url}/v1/complete"
        body = {
            "model": model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens
        }

        try:
            resp = requests.post(url, headers=self._headers(), json=body, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

# ---------------------------
# Modern ChatGPT-Style GUI
# ---------------------------
class ModernChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.client = AgentRouterClaudeClient(self.config)
        self.conversations = []
        self.current_conversation = None
        
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        # Main window configuration
        self.root.title("Claude AI Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create main container
        self.create_sidebar()
        self.create_main_area()
        self.create_menu()

    def create_sidebar(self):
        # Sidebar frame
        self.sidebar = tk.Frame(self.root, width=250, bg="#2c2c2c")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        self.sidebar.grid_propagate(False)
        
        # New chat button
        new_chat_btn = tk.Button(
            self.sidebar, 
            text="+ New Chat", 
            command=self.new_conversation,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=20,
            pady=10
        )
        new_chat_btn.pack(fill="x", padx=10, pady=10)
        
        # Settings button
        settings_btn = tk.Button(
            self.sidebar,
            text="⚙️ Settings",
            command=self.open_settings,
            bg="#666666",
            fg="white",
            font=("Arial", 10),
            relief="flat",
            padx=20,
            pady=8
        )
        settings_btn.pack(fill="x", padx=10, pady=(0, 10))
        
        # Conversations list
        conversations_frame = tk.Frame(self.sidebar, bg="#2c2c2c")
        conversations_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        tk.Label(
            conversations_frame, 
            text="Recent Chats", 
            bg="#2c2c2c", 
            fg="white", 
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Scrollable conversations list
        self.conversations_listbox = tk.Listbox(
            conversations_frame,
            bg="#3c3c3c",
            fg="white",
            selectbackground="#4CAF50",
            font=("Arial", 9),
            relief="flat",
            borderwidth=0
        )
        self.conversations_listbox.pack(fill="both", expand=True)
        self.conversations_listbox.bind("<<ListboxSelect>>", self.on_conversation_select)

    def create_main_area(self):
        # Main chat area
        self.main_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Chat display area
        self.chat_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Chat messages area with custom styling
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            state='disabled',
            bg="#1a1a1a",
            fg="white",
            font=("Arial", 11),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=20
        )
        self.chat_area.grid(row=0, column=0, sticky="nsew")
        
        # Configure text tags for styling
        self.chat_area.tag_configure("user", foreground="#4CAF50", font=("Arial", 11, "bold"))
        self.chat_area.tag_configure("assistant", foreground="#2196F3", font=("Arial", 11))
        self.chat_area.tag_configure("timestamp", foreground="#888888", font=("Arial", 9))
        self.chat_area.tag_configure("error", foreground="#F44336", font=("Arial", 11))
        
        # Input area
        self.create_input_area()

    def create_input_area(self):
        # Input container
        input_frame = tk.Frame(self.main_frame, bg="#2c2c2c", height=80)
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_propagate(False)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input field with modern styling
        self.entry = tk.Text(
            input_frame,
            height=2,
            bg="#3c3c3c",
            fg="white",
            font=("Arial", 11),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=10,
            wrap=tk.WORD
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.entry.bind("<Return>", self.on_enter_press)
        self.entry.bind("<KeyPress>", self.on_key_press)
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=5
        )
        self.send_button.grid(row=0, column=1, padx=(0, 10), pady=10)
        
        # Status label
        self.status_label = tk.Label(
            input_frame,
            text="Ready",
            bg="#2c2c2c",
            fg="#888888",
            font=("Arial", 9)
        )
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

    def create_menu(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Chat", command=self.new_conversation)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.open_docs)

    def apply_theme(self):
        # Apply dark theme colors
        theme = self.config.get("theme")
        if theme == "dark":
            self.root.configure(bg="#1a1a1a")
        else:
            self.root.configure(bg="#ffffff")

    def new_conversation(self):
        """Start a new conversation"""
        self.current_conversation = {
            "id": len(self.conversations),
            "title": "New Chat",
            "messages": [],
            "created_at": datetime.now()
        }
        self.conversations.append(self.current_conversation)
        self.update_conversations_list()
        self.clear_chat_area()
        self.entry.focus()

    def update_conversations_list(self):
        """Update the conversations list in sidebar"""
        self.conversations_listbox.delete(0, tk.END)
        for conv in reversed(self.conversations[-10:]):  # Show last 10 conversations
            title = conv["title"][:30] + "..." if len(conv["title"]) > 30 else conv["title"]
            self.conversations_listbox.insert(0, title)

    def on_conversation_select(self, event):
        """Handle conversation selection from sidebar"""
        selection = self.conversations_listbox.curselection()
        if selection:
            index = len(self.conversations) - 1 - selection[0]
            if 0 <= index < len(self.conversations):
                self.current_conversation = self.conversations[index]
                self.load_conversation()

    def load_conversation(self):
        """Load selected conversation into chat area"""
        if not self.current_conversation:
            return
        
        self.clear_chat_area()
        for message in self.current_conversation["messages"]:
            self.display_message(message["role"], message["content"], message.get("timestamp"))

    def clear_chat_area(self):
        """Clear the chat area"""
        self.chat_area.configure(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.configure(state='disabled')

    def display_message(self, role, content, timestamp=None):
        """Display a message in the chat area with proper styling"""
        self.chat_area.configure(state='normal')
        
        # Add timestamp
        if timestamp:
            self.chat_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add role and content
        if role == "user":
            self.chat_area.insert(tk.END, "You: ", "user")
        else:
            self.chat_area.insert(tk.END, "Claude: ", "assistant")
        
        self.chat_area.insert(tk.END, f"{content}\n\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def on_enter_press(self, event):
        """Handle Enter key press"""
        if event.state & 0x4:  # Ctrl+Enter
            self.send_message()
        return "break"

    def on_key_press(self, event):
        """Handle key press events"""
        if event.keysym == "Return" and not (event.state & 0x4):
            return "break"

    def send_message(self):
        """Send a message to Claude"""
        user_message = self.entry.get("1.0", tk.END).strip()
        if not user_message:
            return

        # Clear input
        self.entry.delete("1.0", tk.END)
        
        # Create new conversation if none exists
        if not self.current_conversation:
            self.new_conversation()

        # Add user message to conversation
        timestamp = datetime.now().strftime("%H:%M")
        self.current_conversation["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": timestamp
        })
        
        # Display user message
        self.display_message("user", user_message, timestamp)
        
        # Update conversation title if it's the first message
        if len(self.current_conversation["messages"]) == 1:
            self.current_conversation["title"] = user_message[:30] + "..." if len(user_message) > 30 else user_message
            self.update_conversations_list()

        # Update status
        self.status_label.config(text="Claude is thinking...", fg="#FF9800")
        self.send_button.config(state="disabled")
        
        # Get response in background thread
        threading.Thread(target=self.get_response, args=(user_message,), daemon=True).start()

    def get_response(self, prompt):
        """Get response from Claude API"""
        try:
            response = self.client.complete(prompt)
            text = response.get("completion", "").strip()
            
            if not text:
                text = "I apologize, but I couldn't generate a response. Please try again."
            
            # Add assistant message to conversation
            timestamp = datetime.now().strftime("%H:%M")
            self.current_conversation["messages"].append({
                "role": "assistant",
                "content": text,
                "timestamp": timestamp
            })
            
            # Display response
            self.root.after(0, lambda: self.display_message("assistant", text, timestamp))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.display_message("assistant", error_msg, "error"))
        
        finally:
            # Reset UI state
            self.root.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        """Reset UI state after response"""
        self.status_label.config(text="Ready", fg="#888888")
        self.send_button.config(state="normal")
        self.entry.focus()

    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg="#2c2c2c")
        settings_window.resizable(False, False)
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        tk.Label(settings_window, text="API Configuration", bg="#2c2c2c", fg="white", font=("Arial", 14, "bold")).pack(pady=20)
        
        # Base URL
        tk.Label(settings_window, text="Base URL:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=20)
        url_entry = tk.Entry(settings_window, width=50)
        url_entry.pack(padx=20, pady=(0, 10))
        url_entry.insert(0, self.config.get("base_url"))
        
        # Auth Token
        tk.Label(settings_window, text="Auth Token:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=20)
        token_entry = tk.Entry(settings_window, width=50, show="*")
        token_entry.pack(padx=20, pady=(0, 10))
        token_entry.insert(0, self.config.get("auth_token"))
        
        # Model
        tk.Label(settings_window, text="Model:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=20)
        model_var = tk.StringVar(value=self.config.get("model"))
        model_combo = ttk.Combobox(settings_window, textvariable=model_var, width=47)
        model_combo['values'] = ("claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307")
        model_combo.pack(padx=20, pady=(0, 10))
        
        # Max Tokens
        tk.Label(settings_window, text="Max Tokens:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=20)
        tokens_entry = tk.Entry(settings_window, width=50)
        tokens_entry.pack(padx=20, pady=(0, 20))
        tokens_entry.insert(0, str(self.config.get("max_tokens")))
        
        # Save button
        def save_settings():
            self.config.set("base_url", url_entry.get())
            self.config.set("auth_token", token_entry.get())
            self.config.set("model", model_var.get())
            try:
                self.config.set("max_tokens", int(tokens_entry.get()))
            except ValueError:
                messagebox.showerror("Error", "Max tokens must be a number")
                return
            
            # Recreate client with new config
            self.client = AgentRouterClaudeClient(self.config)
            settings_window.destroy()
            messagebox.showinfo("Success", "Settings saved successfully!")
        
        tk.Button(settings_window, text="Save", command=save_settings, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Claude AI Assistant\n\nA modern ChatGPT-style interface for Claude AI\nvia AgentRouter API\n\nVersion 2.0")

    def open_docs(self):
        """Open documentation"""
        webbrowser.open("https://docs.anthropic.com/")

# ---------------------------
# Main entry
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatbotGUI(root)
    root.mainloop()
