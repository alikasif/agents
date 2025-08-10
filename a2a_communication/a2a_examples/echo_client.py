from python_a2a import A2AClient, Message, TextContent, MessageRole


def read_incident_chat_file(file_path):
    """Read the incident chat file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def run_client():

    chat = read_incident_chat_file("a2a_communication/incidents_transcript/incident_1.txt")
    #print(f"Chat content: {chat}")

    # triage = read_incident_chat_file("a2a_communication/incidents_transcript/incident_1_triage.txt")    

    # chat_triage = f"incident Chat: {chat}\n\n" + f"incident Triage: {triage}"

    """Run the A2A client to communicate with the Incident Postmortem Agent."""
    # Create a [Python A2A](python-a2a.html) client to talk to our agent
    client = A2AClient("http://localhost:5000/a2a")

    # Send a message using [Python A2A](python-a2a.html)
    message = Message(
        content=TextContent(text=chat),
        role=MessageRole.USER
    )
    response = client.send_message(message)

    # Print the response from our [Python A2A](python-a2a.html) agent
    print(f"Agent says: {response}")


if __name__ == "__main__":
    run_client()
    # This will start the A2A client and send a message to the Incident Postmortem Agent.