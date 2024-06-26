# Comments explaining the basics are in the helloLMStudio file. This file is a more advanced version and only comments the new features.
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

#TODO: Replace the modelID with the one you see in LMStudio under local server.
modelID = "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF"

chatHistory =[{"role": "system",
           "content":
               '''You are a helpful, smart and efficient AI assistant. You always fulfill the user's requests to the best of your ability but keep your answears short.'''
           },]

print("Welcome Message: \nYou can now talk to the primary assistant (Agent 1) with model name " + modelID + " and ask anything. Agent 2 is designed to analyze the mood of the conversation after each interaction.")
print("Mood of Conversation: not analysed yet")
print("User:")
user_input = input("")
chatHistory.append({"role": "user", "content": user_input})

while True:

    ##################### First Agent (User Assistent) #####################

    completion = client.chat.completions.create(
        model=modelID,
        messages=chatHistory,
        temperature=0.7,
        max_tokens=800,
        stream=True,
    )
    new_message = {"role": "assistant", "content": ""}

    print("\nAgent 1: ")
    for chunk in completion:
        newestResponsePart = chunk.choices[0].delta
        if newestResponsePart.content:
            print(newestResponsePart.content, end="", flush=True)
            new_message["content"] += newestResponsePart.content

    chatHistory.append(new_message)

    ##################### Second Agent (Analyser) #####################
    # The second agent is designed to analyze the mood it's output is only shown to the user but not to agent 1.

    # Define the system prompt for the second agent
    system_prompt_second_agent = {"role": "system",
                                  "content": "You are a helpful, smart and efficient AI assistant. Your only task is to analyze the mood of a conversation."}

    # Create a new list to store only user and assistant (agent 1) messages. Basically we only filter out the system messages.
    conversation_only = [f"{message['role']}: {message['content']}" for message in chatHistory if
                         message['role'] in ['user', 'assistant']]

    # Extract the 'content' from each user and assistant (agent 1) messages and join them with a comma
    conversation_content = ', '.join(conversation_only)

    # Insert the string into the simulated user message. We create a user massage because the LLM was trained on getting a sytem message first, and then always a user message it tries to answear.
    # Since Agent 2 has no user it interacts with we create a synthetic user message from the content of the conversation between the user and the agent 1 and combine it with the task to analyse the conversation. Here we could give the second Agend any task.
    # TODO Give agent 2 the task you want him to performe. You can also instantiate more agents with unique tasks but each agent will reduce the speed of the conversation since they all access the same LLM one after another.
    simulated_user_message = {"role": "user",
                      "content": f"Analyze the following text and analyse its overall mood: '{conversation_content}'. The output should be one short sentance use for example words like: happy, sad, excited, neutral, etc. The 5 typical emotions are happiness, sadness, disgust, fear, surprise, anger or emotionless. Here is the conversation for you to analyse: '{conversation_content}'."}

    # Use conversation_only and system_prompt_second_agent when creating the completion
    completion = client.chat.completions.create(
        model=modelID,
        messages=[system_prompt_second_agent, simulated_user_message],
        temperature=0.2,
        max_tokens=800,  # Limit the response to 50 tokens
        stream=True,
    )
    mood_message = {"role": "assistant", "content": ""}

    print("\nAgent 2 (Mood of Conversation): ")
    for chunk in completion:
        newestResponsePart = chunk.choices[0].delta
        #print("\nnewestResponsePart " + str(newestResponsePart))
        if newestResponsePart.content:
            print(newestResponsePart.content, end="", flush=True)
            mood_message["content"] += newestResponsePart.content

    ##################### User Input #####################

    print("\nUser:")
    chatHistory.append({"role": "user", "content": input("")})