import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self, model_path=None):
        # Default to Phi-3-mini-4k-instruct-q4.gguf
        default_model = "Phi-3-mini-4k-instruct-q4.gguf"
        self.model_path = model_path or str(Path.home() / ".studyai_models" / default_model)
        self.llm = None
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Phi-3 model with CPU optimizations - n_ctx=4096."""
        try:
            from llama_cpp import Llama
            
            if not os.path.exists(self.model_path):
                logger.warning("Model not found at %s", self.model_path)
                self.available = False
                return
            
            # Dynamic thread allocation
            cpu_count = os.cpu_count() or 4
            n_threads = min(6, cpu_count)
            
            # Initialize with 4096 context (matching Phi-3 training)
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,           # 4096 context window (user requested)
                n_threads=n_threads,
                n_batch=512,
                verbose=False
            )
            self.available = True
            logger.info("Phi-3 model loaded with %d threads, 4096 context", n_threads)
        except ImportError:
            logger.warning("llama-cpp-python not installed")
            self.available = False
        except Exception as e:
            logger.error("Error initializing Phi-3 model: %s", str(e))
            self.available = False
    
    def generate_response(self, prompt, context="", history=None):
        """Generate AI response - safe for JS bridge (no recursion)."""
        if not (self.available and self.llm):
            return self._fallback_response(prompt, context)
        
        try:
            full_prompt = self._build_prompt(prompt, context, history)
            
            # Count approximate tokens
            token_count = len(full_prompt.split())
            logger.info("Prompt tokens (approx): %d", token_count)
            
            # Make sure total tokens < 4096
            max_response = min(256, 4096 - token_count - 100)
            if max_response < 50:
                max_response = 50
            
            # Generate with strict parameters
            output = self.llm(
                full_prompt,
                max_tokens=max_response,
                temperature=0.1,      # Low for precision
                top_p=0.9,
                repeat_penalty=1.2,  # Stop repetition
                stop=["<|end|>", "<|user|>", "<|system|>"]
            )
            
            response = output['choices'][0]['text'].strip()
            
            # Clean up response
            for stop_token in ["<|end|>", "<|user|>", "<|system|>"]:
                if stop_token in response:
                    response = response.split(stop_token)[0].strip()
            
            return {
                "status": "success",
                "response": response,
                "model": "Phi-3-mini-4k"
            }
        except Exception as e:
            logger.error("Error generating response: %s", str(e))
            return self._fallback_response(prompt, context)
    
    def _build_prompt(self, question, context, history=None):
        """Build prompt using Phi-3 specific template - aggressive truncation."""
        parts = []
        
        # System prompt (short and strict)
        system_prompt = ("You are a precise academic tutor. Answer ONLY from the provided context. "
                       "If the answer is not in the context, say 'I don't have that information in the document.' "
                       "Be concise and accurate. Do not repeat words or phrases.")
        parts.append(f"<|system|>{system_prompt}<|end|>")
        
        # Add conversation history (last 2 exchanges to save tokens)
        if history:
            for msg in history[-4:]:  # Last 4 messages (2 exchanges)
                role = "user" if msg['role'] == 'user' else "assistant"
                content = msg['content']
                # Truncate individual messages aggressively
                if len(content.split()) > 50:
                    content = ' '.join(content.split()[:50]) + "..."
                parts.append(f"<|{role}|>{content}<|end|>")
        
        # Build current user message with context
        user_message_parts = []
        
        # Add context (truncate to ~1500 tokens to leave room)
        if context:
            max_context = 1500
            context_words = context.split()
            if len(context_words) > max_context:
                context = ' '.join(context_words[:max_context]) + "..."
            user_message_parts.append(f"Context:\n{context}")
        
        # Add question
        user_message_parts.append(f"Question: {question}")
        user_message = "\n".join(user_message_parts)
        
        parts.append(f"<|user|>{user_message}<|end|>")
        
        # Assistant start token
        parts.append("<|assistant|>")
        
        return "\n".join(parts)
    
    def _fallback_response(self, prompt, context=""):
        """Fallback response when model is not available."""
        context_msg = ""
        if context:
            preview = context[:200] + "..." if len(context) > 200 else context
            context_msg = f"\n\nFrom your document:\n{preview}"
        
        return {
            "status": "fallback",
            "response": "AI model not available. To enable full AI features:\n"
                       "1. Install llama-cpp-python: pip install llama-cpp-python\n"
                       f"2. Download Phi-3-mini-4k-instruct-q4.gguf to: {self.model_path}\n"
                       f"Your question: '{prompt[:100]}...'{context_msg}",
            "model": "fallback"
        }
    
    def is_available(self):
        """Check if model is available."""
        return self.available
