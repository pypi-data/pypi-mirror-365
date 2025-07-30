"""
AI Helper Agent CLI Module
Interactive command-line interface with conversation history and message trimming
"""

import os
import sys
import asyncio
import getpass
from typing import Dict, Any, Optional
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from .core import InteractiveAgent
from .config import config
from .security import security_manager

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


class AIHelperCLI:
    """Enhanced CLI with LangChain conversation history and trimming"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.api_key: Optional[str] = None
        self.llm: Optional[ChatGroq] = None
        self.chain = None
        self.workspace_path = Path.cwd()
        
        # LangChain conversation setup
        self.conversation_chain = None
        self.trimmer = None
        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for session"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def setup_api_key(self) -> bool:
        """Setup API key with user interaction"""
        print("🤖 AI Helper Agent - Interactive CLI")
        print("=" * 50)
        
        # Check if API key exists in environment
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if self.api_key:
            print(f"✅ Found GROQ_API_KEY in environment")
            return True
        
        print("🔑 Groq API Key required for AI Helper Agent")
        print("You can get a free API key at: https://groq.com/")
        print()
        
        while True:
            try:
                self.api_key = getpass.getpass("Enter your Groq API key: ").strip()
                
                if not self.api_key:
                    print("❌ API key cannot be empty. Please try again.")
                    continue
                
                # Test the API key
                test_llm = ChatGroq(
                    model="llama3-8b-8192",
                    temperature=0.1,
                    api_key=self.api_key
                )
                
                # Quick test
                print("🔄 Testing API key...")
                response = test_llm.invoke([HumanMessage(content="Hello")])
                
                if response and response.content:
                    print("✅ API key validated successfully!")
                    # Store in environment for this session
                    os.environ["GROQ_API_KEY"] = self.api_key
                    return True
                else:
                    print("❌ Invalid API key. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled. Goodbye!")
                return False
            except Exception as e:
                print(f"❌ Error testing API key: {e}")
                print("Please check your API key and try again.")
                continue
    
    def setup_llm_and_chain(self):
        """Setup LLM and conversation chain with history"""
        try:
            # Initialize LLM
            self.llm = ChatGroq(
                model="llama3-8b-8192",
                temperature=0.1,
                api_key=self.api_key
            )
            
            # Setup message trimmer (keep last 8 messages + system)
            self.trimmer = trim_messages(
                max_tokens=4000,  # Adjust based on model limits
                strategy="last",
                token_counter=self.llm,
                include_system=True,
                allow_partial=False,
                start_on="human"
            )
            
            # Create prompt template with history
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            # Create the chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Add trimming to the chain
            chain_with_trimming = (
                RunnablePassthrough.assign(
                    messages=lambda x: self.trimmer.invoke(x["messages"])
                )
                | chain
            )
            
            # Wrap with message history
            self.conversation_chain = RunnableWithMessageHistory(
                chain_with_trimming,
                self.get_session_history,
                input_messages_key="messages",
                history_messages_key="messages",
            )
            
            print("✅ AI Helper Agent initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize AI Helper: {e}")
            return False
        
        return True
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return """You are an expert AI programming assistant specializing in helping developers and students with:

🔧 CODE ANALYSIS & DEBUGGING
- Analyze code for bugs, syntax errors, and logic issues
- Provide detailed explanations and fixes
- Suggest best practices and optimizations

📚 LEARNING SUPPORT  
- Help students understand programming concepts
- Explain code step-by-step
- Provide examples and exercises

🛠️ DEVELOPMENT ASSISTANCE
- Help with algorithm design and implementation
- Code review and refactoring suggestions
- Architecture and design pattern advice

📁 FILE OPERATIONS
- Analyze files in the current workspace
- Create, modify, and organize code files
- Project structure recommendations

INTERACTION GUIDELINES:
1. Always provide clear, educational explanations
2. Use examples to illustrate concepts
3. Ask clarifying questions when needed
4. Break down complex problems into smaller steps
5. Encourage best practices and clean code
6. Be patient and supportive for learning

COMMANDS YOU CAN HELP WITH:
- analyze <filename> - Analyze a specific file
- fix <filename> - Suggest fixes for a file
- explain <concept> - Explain programming concepts
- create <filename> - Help create new files
- review - Review code quality
- help - Show available commands

Current workspace: """ + str(self.workspace_path) + """

I'm here to help you become a better programmer! What can I assist you with today?"""
    
    async def handle_command(self, user_input: str) -> str:
        """Handle user commands and return AI response"""
        try:
            # Special command handling
            if user_input.lower().startswith('analyze '):
                return await self._handle_analyze_command(user_input[8:].strip())
            elif user_input.lower().startswith('fix '):
                return await self._handle_fix_command(user_input[4:].strip())
            elif user_input.lower().startswith('create '):
                return await self._handle_create_command(user_input[7:].strip())
            elif user_input.lower() in ['help', '/help', '?']:
                return self._get_help_text()
            elif user_input.lower().startswith('workspace '):
                return self._handle_workspace_command(user_input[10:].strip())
            
            # Regular conversation with history
            config = {"configurable": {"session_id": self.session_id}}
            
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            return response
            
        except Exception as e:
            return f"❌ Error processing your request: {e}"
    
    async def _handle_analyze_command(self, filename: str) -> str:
        """Handle file analysis command"""
        try:
            file_path = self.workspace_path / filename
            
            if not file_path.exists():
                return f"❌ File not found: {filename}\nCurrent workspace: {self.workspace_path}"
            
            if not security_manager.is_file_accessible(str(file_path)):
                return f"❌ Access denied to file: {filename}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use InteractiveAgent for analysis
            agent = InteractiveAgent(api_key=self.api_key, workspace_path=str(self.workspace_path))
            result = await agent.analyze_code(content, filename)
            
            if result["success"]:
                return f"📊 Analysis of {filename}:\n\n{result['analysis']}"
            else:
                return f"❌ Analysis failed: {result['error']}"
                
        except Exception as e:
            return f"❌ Error analyzing file: {e}"
    
    async def _handle_fix_command(self, filename: str) -> str:
        """Handle file fix command"""
        try:
            file_path = self.workspace_path / filename
            
            if not file_path.exists():
                return f"❌ File not found: {filename}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            agent = InteractiveAgent(api_key=self.api_key, workspace_path=str(self.workspace_path))
            result = await agent.fix_code(content, filename=filename)
            
            if result["success"]:
                return f"🔧 Fixed version of {filename}:\n\n```python\n{result['fixed_code']}\n```\n\nSave this as {filename}_fixed.py?"
            else:
                return f"❌ Fix failed: {result['error']}"
                
        except Exception as e:
            return f"❌ Error fixing file: {e}"
    
    async def _handle_create_command(self, filename: str) -> str:
        """Handle file creation command"""
        return f"📝 I can help you create {filename}. What should this file contain? Describe the functionality you need."
    
    def _handle_workspace_command(self, path: str) -> str:
        """Handle workspace change command"""
        try:
            new_path = Path(path).resolve()
            if new_path.exists() and new_path.is_dir():
                self.workspace_path = new_path
                return f"📂 Workspace changed to: {self.workspace_path}"
            else:
                return f"❌ Directory not found: {path}"
        except Exception as e:
            return f"❌ Error changing workspace: {e}"
    
    def _get_help_text(self) -> str:
        """Get help text"""
        return """🤖 AI Helper Agent - Available Commands:

📁 FILE OPERATIONS:
  analyze <filename>    - Analyze a code file for issues
  fix <filename>        - Get fixed version of a file
  create <filename>     - Get help creating a new file
  
🛠️ WORKSPACE:
  workspace <path>      - Change current workspace directory
  
💬 CONVERSATION:
  Just type naturally to chat with the AI assistant!
  Examples:
  - "Explain recursion in Python"
  - "How do I handle exceptions?"
  - "What's the difference between lists and tuples?"
  - "Help me debug this function"
  
📚 LEARNING:
  - Ask about programming concepts
  - Request code examples
  - Get explanations of algorithms
  - Code review and best practices
  
⚙️ SYSTEM:
  help or ?            - Show this help
  quit, exit, bye      - Exit the program
  
Current workspace: """ + str(self.workspace_path) + """
Conversation history: Keeping last 8 messages with automatic trimming"""
    
    def show_welcome(self):
        """Show welcome message"""
        print("\n🎉 Welcome to AI Helper Agent!")
        print("=" * 50)
        print("🚀 Your intelligent programming assistant")
        print(f"📂 Workspace: {self.workspace_path}")
        print(f"🔄 Session: {self.session_id}")
        print("\nType 'help' for commands or just ask me anything!")
        print("Type 'quit' to exit")
        print("-" * 50)
    
    async def run_interactive_session(self):
        """Run the main interactive session"""
        self.show_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🔵 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for using AI Helper Agent! Happy coding!")
                    break
                
                # Process the input
                print("🤔 Thinking...")
                response = await self.handle_command(user_input)
                print(f"\n🤖 AI Helper:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again or type 'help' for assistance.")
    
    async def start(self):
        """Start the CLI application"""
        try:
            # Setup API key
            if not self.setup_api_key():
                return
            
            # Setup LLM and chains
            if not self.setup_llm_and_chain():
                return
            
            # Start interactive session
            await self.run_interactive_session()
            
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            sys.exit(1)


def main():
    """Main entry point for the CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Interactive Programming Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper-agent                    # Start interactive session
  ai-helper-agent --session mywork  # Start with named session
  ai-helper-agent --workspace ./src  # Start in specific workspace
        """
    )
    
    parser.add_argument(
        "--session", "-s",
        default="default",
        help="Session ID for conversation history"
    )
    
    parser.add_argument(
        "--workspace", "-w",
        default=".",
        help="Workspace directory path"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent CLI v1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance
        cli = AIHelperCLI(session_id=args.session)
        
        # Set workspace
        workspace_path = Path(args.workspace).resolve()
        if workspace_path.exists():
            cli.workspace_path = workspace_path
        else:
            print(f"⚠️  Workspace directory not found: {args.workspace}")
            print(f"Using current directory: {cli.workspace_path}")
        
        # Start the application
        asyncio.run(cli.start())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
