from llama_cpp import Llama

class ChatModel:
    def __init__(self, model_path, chat_format):
        self.model_path = model_path
        self.chat_format = chat_format
        self.llm = Llama(model_path=model_path, chat_format=chat_format)

    def load_model(self, model_path, chat_format):
        self.llm = Llama(model_path=model_path, chat_format=chat_format)
        self.model_path = model_path
        self.chat_format = chat_format

    def generate_response(self, user_question):
        # Create a chat completion by providing messages
        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a story writing assistant."},
                {"role": "user", "content": user_question}
            ]
        )

        # Extracting the generated response
        generated_response = response['choices'][0]['message']['content']
        return generated_response