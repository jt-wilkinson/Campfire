# Campfire 1.0
# Demonstration purposes for Joshua Wilkinson

import openai
import os
import json

# Set your OpenAI API key here
openai.api_key = 'YOU-NEED-AN-API-KEY'


# Function to query OpenAI
def query_openai(prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Only provide Python code for the given prompt, and nothing else. Do not provide any explanations or comments under any circumstances."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Function to load sub-applications
def load_subapplications():
    if os.path.exists('subapplications.json'):
        with open('subapplications.json', 'r') as f:
            return json.load(f)
    return {}

# Function to save sub-applications
def save_subapplications(subapps):
    with open('subapplications.json', 'w') as f:
        json.dump(subapps, f)

# Function to run the main menu
def main_menu():
    subapplications = load_subapplications()
    
    while True:
        print("1. Query OpenAI")
        print("2. Run a sub-application")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            prompt = input("Enter your query for OpenAI: ")
            response = query_openai(prompt)
            print(f"OpenAI Response: {response}")

            # Ask if the response should be added as a sub-application
            add_subapp = input("Do you want to add this as a sub-application? (yes/no): ").strip().lower()
            if add_subapp == 'yes':
                subapp_name = input("Enter a name for the sub-application: ").strip()
                subapplications[subapp_name] = response
                save_subapplications(subapplications)
                print(f"Sub-application '{subapp_name}' added.")
        
        elif choice == '2':
            if not subapplications:
                print("No sub-applications available.")
            else:
                print("Available sub-applications:")
                for subapp in subapplications:
                    print(f"- {subapp}")
                subapp_name = input("Enter the name of the sub-application to run: ").strip()
                if subapp_name in subapplications:
                    print(f"Running '{subapp_name}':")
                    exec(subapplications[subapp_name])
                else:
                    print(f"Sub-application '{subapp_name}' not found.")

        elif choice == '3':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()