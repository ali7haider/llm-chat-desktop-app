from llama_cpp import Llama
llm = Llama(model_path="./stablelm-zephyr-3b.Q3_K_S.gguf", chat_format="llama-2")  # Set chat_format according to the model you are using

def generate_response2(user_question):
        # Create a chat completion by providing messages
        print("generate Func")
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a story writing assistant."},
                {"role": "user", "content": user_question}
            ]
        )
        print(response)

        # Extracting the generated response
        generated_response = response['choices'][0]['message']['content']
        return generated_response
