from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from chat_api_connector import ChatAPIConnector
import os

# Define the KV string for the UI layout
Builder.load_string('''
<ChatLayout>:
    chat_history: chat_history
    message_input: message_input
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 5
        
        ScrollView:
            Label:
                id: chat_history
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: 10, 10
                
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 5
            
            TextInput:
                id: message_input
                multiline: False
                on_text_validate: root.send_message()
                
            Button:
                text: 'Send'
                size_hint_x: None
                width: 100
                on_press: root.send_message()
''')

class ChatLayout(BoxLayout):
    chat_history = ObjectProperty(None)
    message_input = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_connector = ChatAPIConnector()
        # Start a new conversation
        self.current_conversation_id = self.chat_connector.start_conversation()
        
    def send_message(self):
        message = self.message_input.text.strip()
        if message:
            # Add user message to chat history
            self.chat_history.text += f"\nYou: {message}"
            
            # Get response from ChatAPIConnector with conversation ID
            response = self.chat_connector.send_message(
                message, 
                conversation_id=self.current_conversation_id
            )
            
            # Add AI response to chat history
            self.chat_history.text += f"\nAI: {response}\n"
            
            # Clear input field
            self.message_input.text = ""

class ChatApp(App):
    def build(self):
        return ChatLayout()

if __name__ == '__main__':
    ChatApp().run()