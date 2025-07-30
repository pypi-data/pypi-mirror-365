"""Main module with Ollama chat functionality."""

import argparse
import sys
from .terminal_chat import TerminalChat


def hello():
    """Return a hello message."""
    return "Hello, World!"


def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"


def chat(model: str = "gemma3:4b", system: str = "You are a helpful assistant.", 
         analysis_model: str = "gemma3:4b", two_step: bool = True):
    """Start a chat session with Ollama.
    
    Args:
        model: The model to use for chat (default: gemma3:4b)
        system: Optional system message to set context
        analysis_model: Optional separate model for action analysis (defaults to main model)
        two_step: If True, use two-step analysis (action selection, then parameter extraction)
    """
    chat_interface = TerminalChat(
        model=model, 
        system_message=system, 
        analysis_model=analysis_model,
        two_step_analysis=two_step
    )
    chat_interface.run()


def run_vibe_tests(model: str = "gemma3:4b", iterations: int = 1, analysis_model: str = "gemma3:4b"):
    """Run built-in vibe tests.
    
    Args:
        model: The model to use for testing (default: gemma3:4b)
        iterations: Number of iterations per test (default: 1)
        analysis_model: Optional separate model for action analysis (defaults to main model)
    """
    from .vibe_tests import run_vibe_tests as run_tests
    return run_tests(model=model, iterations=iterations, analysis_model=analysis_model)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OllamaPy v0.6.1 - Terminal chat interface for Ollama with AI vibe tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollamapy                          # Start chat with default model (gemma3:4b)
  ollamapy --model llama3.2:3b      # Use a specific model
  ollamapy --analysis-model gemma2:2b --model llama3.2:7b  # Use small model for analysis, large for chat
  ollamapy --two-step               # Use two-step analysis (action, then parameters)
  ollamapy --system "You are a helpful coding assistant"  # Set system message
  ollamapy --vibetest               # Run vibe tests with default settings
  ollamapy --vibetest -n 5          # Run vibe tests with 5 iterations each
  ollamapy --vibetest --model llama3.2:3b -n 3  # Custom model and iterations
  ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b  # Separate models for testing
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemma3:4b",
        help="Model to use for chat responses (default: gemma3:4b)"
    )
    
    parser.add_argument(
        "--analysis-model", "-a",
        help="Model to use for action analysis (defaults to main model if not specified). Use a smaller, faster model for better performance."
    )
    
    parser.add_argument(
        "--system", "-s",
        help="System message to set context for the AI"
    )
    
    parser.add_argument(
        "--two-step",
        action="store_true",
        help="Use two-step analysis: first select action, then extract parameters. Good for very small models."
    )
    
    parser.add_argument(
        "--hello",
        action="store_true",
        help="Just print hello and exit (for testing)"
    )
    
    parser.add_argument(
        "--vibetest",
        action="store_true",
        help="Run built-in vibe tests to evaluate AI decision-making consistency"
    )
    
    parser.add_argument(
        "-n", "--iterations",
        type=int,
        default=1,
        help="Number of iterations for vibe tests (default: 1)"
    )
    
    args = parser.parse_args()
    
    if args.hello:
        print(hello())
        print(greet("Python"))
    elif args.vibetest:
        success = run_vibe_tests(
            model=args.model, 
            iterations=args.iterations, 
            analysis_model=args.analysis_model
        )
        sys.exit(0 if success else 1)
    else:
        chat(
            model=args.model, 
            system=args.system, 
            analysis_model=args.analysis_model,
            two_step=args.two_step
        )


if __name__ == "__main__":
    main()