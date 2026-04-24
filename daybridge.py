from dotenv import load_dotenv
from google_func import service_gmail, read_emails, send_email
from multi_agent import chat
from notion_func import search_notion, parse_notion_results, create_notion_page
from memory_store import load_memory, save_memory
import json

def parse_json_response(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)

def ask_for_json(provider, prompt):
    response = chat(provider, [{"role": "user", "content": prompt}])
    return parse_json_response(response)

load_dotenv()

messages = load_memory() or []

if not messages:
    messages = [
        {
            "role": "system",
            "content": """
You are a helpful assistant that helps the user search and create pages in Notion,sending emails through Gmail, as well as reading and summarizing lengthy emails.
When the user asks you to search Notion, you should use the search_notion tool and parse the results with the parse_notion_results tool, and then use that information to answer the user's question.
When the user asks you to create a Notion page, you should use the create_notion_page tool with the provided title and content, and then confirm with the user that the page was created successfully.
When the user asks you to send an email, you should use the send_email tool with the provided recipient, subject, and body, and then confirm with the user that the email was sent successfully.
When the user asks you to read and summarize emails, you should use the read_emails tool to get the 5 latest emails, and then summarize the sender, subject, and snippet of each email in a concise manner for the user.
If the user asks you something that is not a search query, a request to create a Notion page, a request to send an email, or a request to read and summarize emails, you can just have a normal conversation with them and assist them with any questions they have.
If you are unsure about the user's intent, you can ask clarifying questions to determine whether they want to search Notion, create a Notion page, send an email, or read and summarize emails.
""".strip(),
        }
    ]

if __name__ == "__main__":
    provider = input("Which provider would you like to use? (groq): ").strip().lower()

    if provider != "groq":
        print("Invalid provider. Only groq is currently supported")
        raise SystemExit(1)
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        system_result = None

        classification_prompt = f"""     
Classify the user message into exactly one action:

- search: user wants to find something in Notion
- create: user wants to create a Notion page
- send: user wants to send an email
- read: user wants to read and summarize emails
- chat: general conversation or other questions

Respond with valid JSON only, like:
{{"action": "search"}}

User message: {user_input}
""".strip()
        
        try:
            classification = ask_for_json(provider, classification_prompt)
        except json.decoder.JSONDecodeError:
            print("AI: Sorry, I couldn't classify your request. Please try again.")
            continue

        if not isinstance(classification, dict):
                print("AI: Sorry, I couldn't classify your request properly. Please try again.")
                continue

        action = classification.get("action")
        if action not in {"search", "create", "send", "read", "chat"}:
            print("AI: Sorry, I couldn't determine your request type. Please try again.")
            continue

        if action == "search":
            try:
                search_results = search_notion(user_input)
                parsed_results = parse_notion_results(search_results)
                system_result = f"Notion search results: {parsed_results}"
            except Exception as e:
                print(f"AI: Sorry, I encountered an error while searching Notion: {e}")
                continue
            
        elif action == "create":
            extraction_prompt = f""" 
Extract the page title and content from this message. 

Respond with JSON only:
{{"title": "...", "content": "..."}}

User message: {user_input}
""".strip()
            try:
                extraction = ask_for_json(provider, extraction_prompt)

                if not isinstance(extraction, dict):
                    print("AI: Sorry, I couldn't extract the page details properly. Please try again.")
                    continue

                title = extraction.get("title", "").strip()
                content = extraction.get("content", "").strip()

                if not title or not content:
                    print("AI: I couldn't determine a page title or content from your request.")
                    continue
            except json.decoder.JSONDecodeError:
                print("AI: Sorry, I couldn't extract the title and content from your request. Please try again.")
                continue

            try:
                create_response = create_notion_page(title, content)
            except Exception as e:
                print(f"AI: Notion page creation failed: {e}")
                continue

            if not create_response.get("success"):
                print("AI: Sorry, I couldn't create the Notion page. Please try again.")
                continue

            system_result = f"Notion page created successfully. Title: {title}"
        
        elif action == "send":
            extraction_prompt =  f"""
Extract the recipient, subject, and body from this message. 

Respond with JSON only:
{{"to": "...", "subject": "...", "body": "..."}} 

User message: {user_input}
""".strip()

            try:
                extraction = ask_for_json(provider, extraction_prompt)

                if not isinstance(extraction, dict):
                    print("AI: Sorry, I couldn't extract the email details properly. Please try again.")
                    continue

                to = extraction.get("to", "").strip()
                subject = extraction.get("subject", "").strip()
                body = extraction.get("body", "").strip()

                if not to or not subject or not body:
                    print("AI: I couldn't extract the recipient, subject, and body clearly enough to send the email.")
                    continue    
            except json.decoder.JSONDecodeError:
                print("AI: Sorry, I couldn't extract the recipient, subject, and body from your request. Please try again.")
                continue

            try:
                gmail_service = service_gmail()
                send_response = send_email(gmail_service, to, subject, body)
            except Exception as e:
                print(f"AI: Sorry, I encountered an error while sending the email: {e}")
                continue

            if not send_response.get("success"):
                print("AI: I couldn't send the email.")
                continue

            system_result = f"Email sent successfully to {to} with subject: {subject}"
            
        elif action == "read":
            try:
                gmail_service = service_gmail()
                email_results = read_emails(gmail_service)
            except Exception as e:
                print(f"AI: Sorry, I encountered an error while reading emails: {e}")
                continue

            system_result = f"Email summaries: {email_results}"

        if action == "chat":
            messages.append({"role": "user", "content": user_input})
            conversation_response = chat(provider, messages)
            print(f"AI: {conversation_response}")
            messages.append({"role": "assistant", "content": conversation_response})
            save_memory(messages)
            continue

        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "system", "content": system_result})

        try:
            response = chat(provider, messages)
        except Exception as e:
            print(f"AI: Response generation failed: {e}")
            continue

        print(f"AI: {response}")
        messages.append({"role": "assistant", "content": response})
        save_memory(messages)