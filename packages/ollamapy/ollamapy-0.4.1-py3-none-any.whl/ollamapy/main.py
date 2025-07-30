"""Main module with Ollama chat functionality."""

import argparse
import subprocess
import sys
from .terminal_chat import TerminalChat


def hello():
    """Return a hello message."""
    return "Hello, World!"


def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"


def chat(model: str = "gemma3:4b", system: str = "You are a helpful assistant."):
    """Start a chat session with Ollama.
    
    Args:
        model: The model to use for chat (default: gemma3:4b)
        system: Optional system message to set context
    """
    chat_interface = TerminalChat(model=model, system_message=system)
    chat_interface.run()


def run_vibe_tests(model: str = "gemma3:4b", iterations: int = 1):
    """Run vibe tests using pytest.
    
    Args:
        model: The model to use for testing (default: gemma3:4b)
        iterations: Number of iterations per test (default: 1)
    """
    print(f"🧪 Running vibe tests with model: {model}, iterations: {iterations}")
    print("=" * 60)
    
    # Try to find the tests directory
    import os
    import ollamapy
    
    # Get the package directory
    package_dir = os.path.dirname(ollamapy.__file__)
    
    # Look for tests in multiple possible locations
    possible_test_paths = [
        os.path.join(package_dir, "tests"),  # If tests are included in package
        os.path.join(os.path.dirname(package_dir), "tests"),  # Development setup
        "tests",  # Current directory
    ]
    
    test_path = None
    for path in possible_test_paths:
        if os.path.exists(path) and os.path.isdir(path):
            test_path = path
            break
    
    if not test_path:
        print("❌ Error: Could not find tests directory.")
        print("Running built-in vibe tests instead...")
        return run_builtin_vibe_tests(model, iterations)
    
    # Build pytest command
    pytest_args = [
        "pytest", 
        "-v", 
        "-s",  # Don't capture output so we can see real-time results
        "--tb=short",  # Shorter traceback format
        test_path,
        "-k", "vibe"  # Only run tests with 'vibe' in the name
    ]
    
    # Set environment variables for the test configuration
    os.environ['VIBETEST_MODEL'] = model
    os.environ['VIBETEST_ITERATIONS'] = str(iterations)
    
    try:
        # Run pytest as subprocess
        result = subprocess.run(pytest_args, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install pytest:")
        print("   pip install pytest")
        print("Running built-in vibe tests instead...")
        return run_builtin_vibe_tests(model, iterations)
    except Exception as e:
        print(f"❌ Error running vibe tests: {e}")
        print("Running built-in vibe tests instead...")
        return run_builtin_vibe_tests(model, iterations)


def run_builtin_vibe_tests(model: str = "gemma3:4b", iterations: int = 1):
    """Run built-in vibe tests without pytest dependency."""
    from .terminal_chat import TerminalChat
    
    print(f"🧪 Running built-in vibe tests with model: {model}, iterations: {iterations}")
    
    chat_interface = TerminalChat(model=model)
    
    # Check if Ollama is available
    if not chat_interface.client.is_available():
        print("❌ Error: Ollama server is not running!")
        print("Please start Ollama with: ollama serve")
        return False
    
    # YES direction test
    yes_phrases = [
        "Yes is the direction I would like to go this time",
        "I'm feeling positive about this decision",
        "Absolutely, let's move forward with this",
        "This sounds like a great idea to me",
        "I agree with this approach completely"
    ]
    
    # NO direction test  
    no_phrases = [
        "No, I don't think this is the right path",
        "I disagree with this approach entirely",
        "This doesn't seem like a good idea to me",
        "I'm not feeling confident about this decision",
        "Absolutely not, let's try something else"
    ]
    
    def test_phrases(phrases, expected_result, test_name):
        """Test a set of phrases and return success rate."""
        total_correct = 0
        total_tests = 0
        results = {}
        
        print(f"\n🧪 {test_name} Test (Model: {model})")
        print("=" * 80)
        
        for phrase in phrases:
            phrase_correct = 0
            
            for i in range(iterations):
                try:
                    chosen_function = chat_interface.analyze_with_ai(phrase)
                    if chosen_function == expected_result:
                        phrase_correct += 1
                    total_tests += 1
                except Exception as e:
                    print(f"Error testing phrase '{phrase}' iteration {i+1}: {e}")
                    continue
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate
            }
            total_correct += phrase_correct
            
            # Print individual results
            print(f"Phrase: '{phrase[:50]}{'...' if len(phrase) > 50 else ''}'")
            print(f"Success: {phrase_correct}/{iterations} ({success_rate:.1f}%)")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        
        return overall_success_rate >= 60.0
    
    # Run both tests
    yes_success = test_phrases(yes_phrases, "yes", "YES Direction")
    no_success = test_phrases(no_phrases, "no", "NO Direction")
    
    # Final results
    print(f"\n📊 Final Results:")
    print(f"YES Direction Test: {'✅ PASSED' if yes_success else '❌ FAILED'}")
    print(f"NO Direction Test: {'✅ PASSED' if no_success else '❌ FAILED'}")
    
    overall_success = yes_success and no_success
    print(f"Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OllamaPy - Terminal chat interface for Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollamapy                          # Start chat with default model (gemma3:4b)
  ollamapy --model llama3.2:3b      # Use a specific model
  ollamapy --system "You are a helpful coding assistant"  # Set system message
  ollamapy --vibetest               # Run vibe tests with default settings
  ollamapy --vibetest -N 5          # Run vibe tests with 5 iterations each
  ollamapy --vibetest --model llama3.2:3b -N 3  # Custom model and iterations
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemma3:4b",
        help="Model to use for chat or testing (default: gemma3:4b)"
    )
    
    parser.add_argument(
        "--system", "-s",
        help="System message to set context for the AI"
    )
    
    parser.add_argument(
        "--hello",
        action="store_true",
        help="Just print hello and exit (for testing)"
    )
    
    parser.add_argument(
        "--vibetest",
        action="store_true",
        help="Run vibe tests to evaluate AI decision-making consistency"
    )
    
    parser.add_argument(
        "-N", "--iterations",
        type=int,
        default=1,
        help="Number of iterations for vibe tests (default: 1)"
    )
    
    args = parser.parse_args()
    
    if args.hello:
        print(hello())
        print(greet("Python"))
    elif args.vibetest:
        success = run_vibe_tests(model=args.model, iterations=args.iterations)
        sys.exit(0 if success else 1)
    else:
        chat(model=args.model, system=args.system)


if __name__ == "__main__":
    main()