from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv()


@tool(parse_docstring=True)
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email to a recipient.
    
    Args:
        recipient: Email address of the recipient.
        subject: Subject line of the email.
        body: Body content of the email.
    
    Returns:
        Confirmation message.
    """
    return f"Email sent successfully to {recipient}"

config = {"configurable": {"thread_id": "1"}}
agent = create_agent(
    model="openai:gpt-5-nano",
    tools=[send_email],
    system_prompt="You are a helpful assistant for Sydney that can send emails.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"send_email": True})],
    checkpointer=InMemorySaver(), 
)

# Test low stakes email
print("Low stakes email response:")
response = agent.invoke({"messages": {
            "role": "user",
            # "content": "Respond to the following email:From: alice@example.com. Subject: Coffee?. Body: Hey, would you like to grab coffee next week?... and send it as it is"
            "content": "hello"

            }},
            config=config
        )


# check if __interrupt__ is true in response
check_interrupt = response.get("__interrupt__", False)

if check_interrupt:
    print("interrupted for human approval")

    response = agent.invoke(
        Command( 
            resume={"decisions": [{"type": "approve"}]}  # or "reject"
        ),
        config=config # Same thread ID to resume the paused conversation
    )

    # convert response object to dict and print last ai message content
    last_ai_content = response["messages"][-1].content

    print(last_ai_content)

else:
    print("no interruption, response:")
    # print ai message response
    last_ai_content = response["messages"][-1].content
    print(response)
    print(last_ai_content)
