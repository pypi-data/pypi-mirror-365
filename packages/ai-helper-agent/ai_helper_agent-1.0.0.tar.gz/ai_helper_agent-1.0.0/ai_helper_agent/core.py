"""
Interactive AI Helper Agent - Core Module
Provides intelligent code assistance with interactive prompting
"""

import asyncio
import pathlib
import json
from typing import Optional, Dict, Any, List
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from .config import config
from .security import security_manager


class InteractiveAgent:
    """Interactive AI Assistant for Code Analysis and Bug Fixing"""
    
    def __init__(self, llm: Optional[ChatGroq] = None, workspace_path: str = ".", 
                 api_key: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.1):
        """
        Initialize the Interactive Agent
        
        Args:
            llm: Pre-configured LLM instance (optional)
            workspace_path: Path to workspace directory
            api_key: Groq API key (optional, will use env var if not provided)
            model: Model name to use (optional, defaults to llama3-8b-8192)
            temperature: Temperature for AI responses (optional, defaults to 0.1)
        """
        self.api_key = api_key
        self.model = model or "llama3-8b-8192"
        self.temperature = temperature
        self.llm = llm or self._setup_default_llm()
        self.workspace_path = pathlib.Path(workspace_path)
        self.conversation_history = []
        
        # Default system prompt for code assistance
        self.system_prompt = """You are an expert AI programming assistant specializing in:

🔧 CODE ANALYSIS & BUG FIXING
- Analyze Python, JavaScript, TypeScript, and other code
- Identify syntax errors, logic bugs, and performance issues
- Provide complete, working fixes with explanations

📁 FILE OPERATIONS
- Read, analyze, and modify files
- Create new files with proper structure
- Organize code into logical modules

🚀 BEST PRACTICES
- Follow language-specific conventions
- Implement proper error handling
- Add meaningful comments and documentation
- Suggest improvements and optimizations

INTERACTION RULES:
1. Always ask for user confirmation before creating/modifying files
2. Provide clear explanations for all changes
3. Show code previews before implementing
4. Ask clarifying questions when requirements are unclear
5. Offer multiple solutions when appropriate

When the user provides input, analyze their request and:
- If it involves file operations, ask for specific file paths and destinations
- If it's code analysis, show your findings and proposed fixes
- If it's code creation, show the structure and ask for approval
- Always be helpful, clear, and interactive

Current workspace: {workspace_path}
Ready to assist with your coding needs!"""

    def _setup_default_llm(self) -> ChatGroq:
        """Setup default Groq LLM"""
        # Use provided API key or get from config/environment
        api_key = self.api_key or config.get_api_key("groq")
        
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please either:\n"
                # "1. Set GROQ_API_KEY environment variable, or\n"
                "2. Pass api_key parameter: InteractiveAgent(api_key='your_key')"
            )
        
        return ChatGroq(
            model=self.model,
            temperature=self.temperature,
            api_key=api_key
        )

    async def analyze_code(self, code: str, filename: str = "code") -> Dict[str, Any]:
        """Analyze code for issues and improvements"""
        analysis_prompt = f"""
Analyze this {filename} code for:
1. Syntax errors
2. Logic bugs  
3. Performance issues
4. Best practice violations
5. Missing error handling

Code:
```python
{code}
```

Provide a structured analysis with specific line numbers and suggestions.
"""
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt.format(workspace_path=self.workspace_path)),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "analysis": response.content,
                "filename": filename,
                "code_length": len(code)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }

    async def fix_code(self, code: str, issues: str = "", filename: str = "code") -> Dict[str, Any]:
        """Fix code issues and return corrected version"""
        fix_prompt = f"""
Fix this {filename} code. 

Issues to address: {issues if issues else "All detectable bugs and improvements"}

Original code:
```python
{code}
```

Return ONLY the complete fixed Python code. No explanations, just clean, working code.
"""
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt.format(workspace_path=self.workspace_path)),
                HumanMessage(content=fix_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            fixed_code = response.content.strip()
            
            # Clean up response to extract code
            if "```python" in fixed_code:
                start = fixed_code.find("```python") + 9
                end = fixed_code.find("```", start)
                if end != -1:
                    fixed_code = fixed_code[start:end].strip()
            elif "```" in fixed_code:
                start = fixed_code.find("```") + 3
                end = fixed_code.find("```", start)
                if end != -1:
                    fixed_code = fixed_code[start:end].strip()
            
            return {
                "success": True,
                "fixed_code": fixed_code,
                "original_length": len(code),
                "fixed_length": len(fixed_code),
                "filename": filename
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }

    async def chat(self, user_input: str) -> str:
        """Interactive chat with the AI assistant"""
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Build messages with conversation context
            messages = [
                SystemMessage(content=self.system_prompt.format(workspace_path=self.workspace_path))
            ]
            
            # Add recent conversation history (last 10 exchanges)
            for exchange in self.conversation_history[-10:]:
                if exchange["role"] == "user":
                    messages.append(HumanMessage(content=exchange["content"]))
                else:
                    messages.append(SystemMessage(content=f"Assistant: {exchange['content']}"))
            
            response = await self.llm.ainvoke(messages)
            assistant_response = response.content
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read a file from the workspace"""
        try:
            file_path = self.workspace_path / filepath
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "filepath": str(file_path),
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, filepath: str, content: str, confirm: bool = True) -> Dict[str, Any]:
        """Write content to a file (with confirmation and security checks)"""
        try:
            # Security check
            if not security_manager.is_file_accessible(filepath):
                return {"success": False, "error": "Access denied: File not accessible"}
            
            file_path = self.workspace_path / filepath
            
            if confirm and file_path.exists():
                response = input(f"⚠️  File {filepath} already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    return {"success": False, "error": "Operation cancelled by user"}
            
            # Additional confirmation for new files if configured
            if confirm and not file_path.exists():
                response = input(f"📝 Create new file {filepath}? (y/N): ")
                if response.lower() != 'y':
                    return {"success": False, "error": "Operation cancelled by user"}
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": str(file_path),
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self, pattern: str = "*") -> List[str]:
        """List files in workspace matching pattern"""
        try:
            files = []
            for file_path in self.workspace_path.rglob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.workspace_path)
                    files.append(str(relative_path))
            return sorted(files)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def interactive_session(self):
        """Start an interactive session with the AI assistant"""
        print("🤖 AI Helper Agent v1 - Interactive Session")
        print("=" * 50)
        print(f"📂 Workspace: {self.workspace_path.resolve()}")
        print("\nCommands:")
        print("  📝 'analyze <file>' - Analyze a code file")
        print("  🔧 'fix <file>' - Fix bugs in a file")
        print("  📂 'list [pattern]' - List files (optional pattern)")
        print("  💬 Just type anything else to chat")
        print("  🚪 'quit' or 'exit' to end session")
        print("\n" + "=" * 50)
        
        while True:
            try:
                user_input = input("\n🔵 You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Happy coding!")
                    break
                
                # Handle special commands
                if user_input.startswith('analyze '):
                    filename = user_input[8:].strip()
                    result = self.read_file(filename)
                    if result["success"]:
                        print(f"\n📖 Analyzing {filename}...")
                        analysis = asyncio.run(self.analyze_code(result["content"], filename))
                        if analysis["success"]:
                            print(f"🤖 Assistant:\n{analysis['analysis']}")
                        else:
                            print(f"❌ Analysis failed: {analysis['error']}")
                    else:
                        print(f"❌ {result['error']}")
                    continue
                
                elif user_input.startswith('fix '):
                    filename = user_input[4:].strip()
                    result = self.read_file(filename)
                    if result["success"]:
                        print(f"\n🔧 Fixing {filename}...")
                        fix_result = asyncio.run(self.fix_code(result["content"], filename=filename))
                        if fix_result["success"]:
                            fixed_filename = f"{pathlib.Path(filename).stem}_fixed{pathlib.Path(filename).suffix}"
                            
                            # Show preview
                            print(f"\n📄 Fixed code preview:")
                            lines = fix_result["fixed_code"].split('\n')
                            for i, line in enumerate(lines[:10], 1):
                                print(f"   {i:2d}: {line}")
                            if len(lines) > 10:
                                print(f"   ... ({len(lines) - 10} more lines)")
                            
                            # Ask for confirmation
                            confirm = input(f"\n💾 Save as {fixed_filename}? (Y/n): ")
                            if confirm.lower() != 'n':
                                write_result = self.write_file(fixed_filename, fix_result["fixed_code"], confirm=False)
                                if write_result["success"]:
                                    print(f"✅ Saved fixed code to {fixed_filename}")
                                else:
                                    print(f"❌ {write_result['error']}")
                        else:
                            print(f"❌ Fix failed: {fix_result['error']}")
                    else:
                        print(f"❌ {result['error']}")
                    continue
                
                elif user_input.startswith('list'):
                    pattern = user_input[4:].strip() or "*"
                    files = self.list_files(pattern)
                    print(f"\n📂 Files matching '{pattern}':")
                    for f in files[:20]:  # Show first 20
                        print(f"   📄 {f}")
                    if len(files) > 20:
                        print(f"   ... and {len(files) - 20} more files")
                    continue
                
                # Regular chat
                print(f"\n💭 Processing your request...")
                response = asyncio.run(self.chat(user_input))
                print(f"🤖 Assistant:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def create_agent(llm: Optional[ChatGroq] = None, workspace_path: str = ".", 
                 api_key: Optional[str] = None, model: Optional[str] = None, 
                 temperature: float = 0.1) -> InteractiveAgent:
    """
    Create a new AI Helper Agent instance
    
    Args:
        llm: Pre-configured LLM instance (optional)
        workspace_path: Path to workspace directory
        api_key: Groq API key (optional, will use env var if not provided)
        model: Model name to use (optional, defaults to llama3-8b-8192)
        temperature: Temperature for AI responses (optional, defaults to 0.1)
    
    Returns:
        InteractiveAgent instance
    """
    return InteractiveAgent(llm=llm, workspace_path=workspace_path, api_key=api_key, 
                          model=model, temperature=temperature)


# Quick start function for immediate use
def quick_start():
    """Quick start interactive session"""
    agent = create_agent()
    agent.interactive_session()


def main():
    """Main entry point for CLI usage"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Interactive code assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper                    # Start interactive session
  ai-helper analyze file.py    # Analyze a specific file
  ai-helper chat "help me"     # Quick chat command
        """
    )
    
    parser.add_argument(
        "command", 
        nargs="?", 
        choices=["analyze", "chat", "interactive"],
        default="interactive",
        help="Command to execute"
    )
    
    parser.add_argument(
        "target",
        nargs="?", 
        help="File to analyze or message to chat"
    )
    
    parser.add_argument(
        "--workspace", "-w",
        default=".",
        help="Workspace directory path"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent v1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        agent = create_agent(workspace_path=args.workspace)
        
        if args.command == "analyze":
            if not args.target:
                print("Error: Please provide a file to analyze")
                sys.exit(1)
            result = agent.analyze_file(args.target)
            print(result)
            
        elif args.command == "chat":
            if not args.target:
                print("Error: Please provide a message")
                sys.exit(1)
            response = agent.chat(args.target)
            print(response)
            
        else:  # interactive
            agent.interactive_session()
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
