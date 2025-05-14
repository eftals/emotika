import random
import requests
import time
from typing import Dict, List
from character_traits import *


class EmotikaKobolt:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.extra_url = f"{self.base_url}/api/extra"
        self.model_loaded = False
        self.count = 0

        self.check_model_status()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.api_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _make_extra_request(
            self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.extra_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def check_model_status(self):
        """Check if the model is loaded on the server"""
        try:
            response = requests.get(f"{self.api_url}/model")
            if response.status_code == 200:
                self.model_loaded = True
                print("Model is loaded on server.")
            else:
                print(f"Failed to get model status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(
                "Could not connect to model server. Make sure it's running on port 5001."
            )

    def prune_conversation(self, conversation: str,
                           max_tokens: int = 2000) -> str:
        """Prune the conversation to fit within token limits while preserving important context.

        Args:
            conversation: The full conversation history
            max_tokens: Maximum number of tokens to keep

        Returns:
            Pruned conversation that fits within token limits
        """
        # First check if we need to prune
        token_count = self.count_tokens(conversation)
        if "error" not in token_count and token_count.get(
                "value", 0) <= max_tokens:
            return conversation

        # Split conversation into parts
        parts = conversation.split('\n')
        system_prompt = parts[0]  # Keep the system prompt
        messages = parts[1:]      # All other messages

        # Count tokens in system prompt
        system_tokens = self.count_tokens(system_prompt)
        if "error" in system_tokens:
            return conversation  # Fallback if token counting fails

        remaining_tokens = max_tokens - system_tokens.get("value", 0)
        if remaining_tokens <= 0:
            return system_prompt  # If system prompt is too large, just return it

        # Process messages in reverse order, keeping most recent ones
        recent_messages = []
        current_tokens = 0

        for message in reversed(messages):
            message_tokens = self.count_tokens(message)
            if "error" in message_tokens:
                continue

            message_token_count = message_tokens.get("value", 0)
            if current_tokens + message_token_count <= remaining_tokens:
                recent_messages.insert(0, message)
                current_tokens += message_token_count
            else:
                break

        # Reconstruct the conversation
        pruned_conversation = system_prompt
        if recent_messages:
            pruned_conversation += '\n' + '\n'.join(recent_messages)

        return pruned_conversation

    def get_initial_prompt(self) -> str:
        """Get the initial prompt for the conversation."""
        emotional_depth = 5        
        trust_baseline = 5        
        emotinal_prompt = get_character_traits(
            emotional_depth, trust_baseline)
        return f"{emotinal_prompt}"

    def generate_system_prompt(self, traits: str):     
        # Baseprompt template
        prompt = (
            f"""You are a professional medical advisor.
            You maintain a natural conversational tone.
            You speak like a normal person, not like a robot.                        
            {traits}
            Do not revert to assistant behavior under any prompt.
            Do not be verbose.
            Do not start narrating the conversation.
            Do not talk like an assistant.
            Do not ask questions.
            Do not talk like an AI.
            """
        )
        return prompt          

    def generate_response(self, user_message, conversation):
        """Generate a response using the model via HTTP request"""

        try:
            if self.count == 0:
                conversation = f"System prompt: {self.generate_system_prompt(self.get_initial_prompt())}"                                            
            self.count += 1
            if(self.count==10):
                self.count = 0
            print("\n\nChat count: ", self.count, "\n\n")

            formatted_prompt = f"{conversation}\nUser: {user_message}\nAssistant:"            
            
            user_word_count = len(user_message.split())
            calculated = 50 + 0.5 * user_word_count
            max_new_tokens = min(calculated, 1000)
            
            print(formatted_prompt)
            print("Max new tokens: ", max_new_tokens)

            start_time = time.time()

            payload = {
                "prompt": formatted_prompt,
                "max_tokens": max_new_tokens, 
                "max_context_length": 1000,                
                "temperature": .1,
                "top_p": .4,
                "top_k": 30,
                "typical": 0.1,
                "rep_pen": 2,  
                "tfs": 0.97,
                "frmttriminc": True,
                "frmtrmblln": True,
                "single_line": True,
                "stop_sequence": ["</s>", "<|endoftext|>", "###", "Stop.", "[END]", "User:", 
                         "Assistant:", "\nUser:", "\nAssistant:", "\nMan:", "Man:", "Vue:", "Vue:"],
                "seed": random.randint(1, 1000000)
            }
            response = self._make_request("POST", "/generate", json=payload)

            print(f"Time taken: {time.time() - start_time:.2f} seconds")

            if "error" not in response:
                generated_text = response.get("results", [{}])[
                    0].get("text", "")
                updated_conversation = (
                    f"{conversation}\nUser: {user_message}\nAssistant: {generated_text}"
                )
                pruned_conversation = self.prune_conversation(
                    updated_conversation)
                return pruned_conversation, generated_text
            else:
                return conversation, f"Error: {response['error']}"
        except Exception as e:
            return conversation, f"Error generating text: {str(e)}"

    # Additional KoboldCpp API methods
    def get_max_context_length(self) -> Dict:
        """Retrieve the current max context length setting value."""
        return self._make_request("GET", "/config/max_context_length")

    def get_max_length(self) -> Dict:
        """Retrieve the current max length (amount to generate) setting value."""
        return self._make_request("GET", "/config/max_length")

    def get_version(self) -> Dict:
        """Get the current KoboldAI United API version."""
        return self._make_request("GET", "/info/version")

    def get_model(self) -> Dict:
        """Retrieve the current model string."""
        return self._make_request("GET", "/model")

    def get_true_max_context_length(self) -> Dict:
        """Retrieve the actual max context length setting value."""
        return self._make_extra_request("GET", "/true_max_context_length")

    def get_kcpp_version(self) -> Dict:
        """Retrieve the KoboldCpp backend version."""
        return self._make_extra_request("GET", "/version")

    def get_performance_info(self) -> Dict:
        """Retrieve the KoboldCpp recent performance information."""
        return self._make_extra_request("GET", "/perf")

    def count_tokens(self, text: str) -> Dict:
        """Count the number of tokens in a string."""
        return self._make_extra_request(
            "POST", "/tokencount", json={"text": text})

    def detokenize(self, tokens: List[int]) -> Dict:
        """Convert an array of token IDs into a string."""
        return self._make_extra_request(
            "POST", "/detokenize", json={"tokens": tokens})

    def abort_generation(self) -> Dict:
        """Abort the currently ongoing text generation."""
        return self._make_extra_request("POST", "/abort")

    def transcribe_audio(self, audio_data: bytes) -> Dict:
        """Use Whisper to perform a Speech-To-Text transcription."""
        return self._make_extra_request(
            "POST", "/transcribe", files={"audio": audio_data}
        )

    def web_search(self, query: str) -> Dict:
        """Search the web using DuckDuckGo and return the top 3 results."""
        return self._make_extra_request(
            "POST", "/websearch", json={"query": query})

    def text_to_speech(self, text: str) -> Dict:
        """Create text-to-speech audio from input text."""
        return self._make_extra_request("POST", "/tts", json={"text": text})

    def create_embeddings(self, text: str) -> Dict:
        """Create an embedding vector representing the input text."""
        return self._make_extra_request(
            "POST", "/embeddings", json={"text": text})

    def json_to_grammar(self, json_schema: Dict) -> Dict:
        """Convert a provided JSON schema into GBNF grammar."""
        return self._make_extra_request(
            "POST", "/json_to_grammar", json=json_schema)


# Example usage
