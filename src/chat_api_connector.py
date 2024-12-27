from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import dotenv
import os
from typing import List, Optional, Dict
import uuid

dotenv.load_dotenv()

class ChatAPIConnector:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ChatAPIConnector with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either through constructor or OPENAI_API_KEY environment variable")
        
        # Initialize chat model
        self.chat_model = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-mini",
            openai_api_key=self.api_key
        )
        
        # Initialize system message
        self.system_message = SystemMessage(content=(
            "You are a helpful AI assistant that provides clear and concise responses."
        ))
        
        # Setup LangGraph workflow
        self.workflow = StateGraph(state_schema=MessagesState)
        self.memory = MemorySaver()
        
        # Define the model call function
        def call_model(state: MessagesState):
            messages = [self.system_message] + state["messages"]
            response = self.chat_model.invoke(messages)
            return {"messages": state["messages"] + [response]}
        
        # Setup graph workflow
        self.workflow.add_edge(START, "model")
        self.workflow.add_node("model", call_model)
        
        # Compile the workflow with memory
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        # Store active conversations
        self.conversations: Dict[str, str] = {}
    
    def start_conversation(self) -> str:
        """Start a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = conversation_id
        return conversation_id
    
    def send_message(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Send a message to the chat model and get a response."""
        try:
            # Create or get conversation ID
            if conversation_id is None or conversation_id not in self.conversations:
                conversation_id = self.start_conversation()
            
            # Setup config with thread ID
            config = {"configurable": {"thread_id": conversation_id}}
            
            # Create input message
            input_messages = [HumanMessage(message)]
            
            # Get response from the workflow
            output = self.app.invoke({"messages": input_messages}, config)
            
            # Return the last message (AI's response)
            return output["messages"][-1].content
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self, conversation_id: str):
        """Clear the conversation history for a specific conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_all_conversations(self) -> List[str]:
        """Get a list of all active conversation IDs."""
        return list(self.conversations.keys())