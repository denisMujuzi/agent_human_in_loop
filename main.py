from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langgraph.types import Command
from urllib.parse import urlparse
from neo4j import GraphDatabase
from datetime import datetime
import os
from pydantic import BaseModel
import uuid
from enum import Enum


load_dotenv()

# neo4j connection setup
def _normalize_neo4j_uri(raw_uri: str) -> str:
    """Ensure the Neo4j URI includes a supported scheme."""
    parsed = urlparse(raw_uri)
    if parsed.scheme:
        return raw_uri
    # Treat raw host[:port] as bolt URI by default
    return f"bolt://{raw_uri}"

URI = _normalize_neo4j_uri(os.getenv("NEO4J_URI"))
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

driver = GraphDatabase.driver(URI, auth=AUTH)


# create uuid fun
def generate_uuid() -> str:
    return str(uuid.uuid4())


class ExpenseItem(BaseModel):    
    quantity: int
    rate: int
    amount: int
    particulars: str
    userID: int

class ExpenseItemResponse(ExpenseItem):
    id: str
    createdAt: datetime

class EditExpenseItem(BaseModel):
    quantity: int = None
    rate: int = None
    amount: int = None
    particulars: str = None


@tool(parse_docstring=True)
def add_famrer_expenses(expenses: list[ExpenseItem]) -> str:
    """Save user expenses.
    
    Args:
        expenses: List of ExpenseItem objects containing expense details.
    
    Returns:
        Confirmation message.
    """
    with driver.session() as session:
        for expense in expenses:
            expenseID = generate_uuid()
            session.run(
                """
                MERGE (e:Expense {id: $expenseID})
                ON CREATE SET e += {
                    quantity: $quantity,
                    rate: $rate,
                    amount: $amount,
                    particulars: $particulars,
                    userID: $userID,
                    createdAt: datetime()
                }
                """,
                expenseID=expenseID,
                quantity=expense.quantity,
                rate=expense.rate,
                amount=expense.amount,
                particulars=expense.particulars,
                userID=expense.userID,
            )
            

    return f"Successfully added expenses"


# get expenses of a user
@tool(parse_docstring=True)
def get_famrer_expenses(userID: int) -> list[ExpenseItemResponse]:
    """Get user expenses.
    
    Args:
        userID: The ID of the user to retrieve expenses for.
    
    Returns:
        List of ExpenseItemResponse objects containing expense details.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (e:Expense {userID: $userID})
            RETURN e.quantity AS quantity, e.rate AS rate, e.amount AS amount, e.particulars AS particulars, e.createdAt AS createdAt, e.id AS id
            """,
            userID=userID,
        )
        expenses = []
        for record in result:
            expenses.append(
                ExpenseItemResponse(
                    quantity=record["quantity"],
                    rate=record["rate"],
                    amount=record["amount"],
                    particulars=record["particulars"],
                    userID=userID,
                    createdAt=record["createdAt"].isoformat(),
                    id=record["id"]
                )
            )
        if len(expenses) == 0:
            return "No expenses found for the user."
        return expenses


# delete expense by id
@tool(parse_docstring=True)
def delete_famrer_expense(expenseID: str) -> str:
    """Delete a user expense by ID.
    
    Args:
        expenseID: The ID of the expense to delete.
    
    Returns:
        Confirmation message.
    """
    with driver.session() as session:
        session.run(
            """
            MATCH (e:Expense {id: $expenseID})
            DELETE e
            """,
            expenseID=expenseID,
        )
    return f"Successfully deleted expense with ID {expenseID}"


# edit expense by id
@tool(parse_docstring=True)
def edit_famrer_expense(expenseID: str, editData: EditExpenseItem) -> str:
    """Edit a user expense by ID.
    
    Args:
        expenseID: The ID of the expense to edit.
        editData: An EditExpenseItem object containing the fields to update.
    
    Returns:
        Confirmation message.
    """
    with driver.session() as session:
        # Build the SET clause dynamically based on which fields are provided
        set_clauses = []
        params = {"expenseID": expenseID}
        
        if editData.quantity is not None:
            set_clauses.append("e.quantity = $quantity")
            params["quantity"] = editData.quantity
        if editData.rate is not None:
            set_clauses.append("e.rate = $rate")
            params["rate"] = editData.rate
        if editData.amount is not None:
            set_clauses.append("e.amount = $amount")
            params["amount"] = editData.amount
        if editData.particulars is not None:
            set_clauses.append("e.particulars = $particulars")
            params["particulars"] = editData.particulars
        
        if not set_clauses:
            return "No fields to update."
        
        set_clause = ", ".join(set_clauses)
        
        session.run(
            f"""
            MATCH (e:Expense {{id: $expenseID}})
            SET {set_clause}
            """,
            **params,
        )
    return f"Successfully edited expense with ID {expenseID}"


config = {"configurable": {"thread_id": "1"}}
agent = create_agent(
    model="openai:gpt-5-nano",
    tools=[add_famrer_expenses, get_famrer_expenses, delete_famrer_expense, edit_famrer_expense],
    system_prompt="You are a helpful assistant for Sydney(userID:1) that can manage expenses(add, get, delete, edit). You will receive images of receipts and extract relevant information to add the expenses or answer the inquiry. You can ask follow-up questions if you need more information to create the expenses. The amount for the each specfic expense is always written in the last column of the record of the expense int he receipt. ignore the total sum of all expenses on the receipt.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"add_famrer_expenses": True, "edit_famrer_expense": True, "delete_famrer_expense": True, "get_famrer_expenses": False})],
    # checkpointer=InMemorySaver(), 
)

# # Test low stakes email
# print("Low stakes email response:")
# response = agent.invoke({"messages": {
#             "role": "user",
#             # "content": "Respond to the following email:From: alice@example.com. Subject: Coffee?. Body: Hey, would you like to grab coffee next week?... and send it as it is"
#             "content": "hello"

#             }},
#             config=config
#         )


# # check if __interrupt__ is true in response
# check_interrupt = response.get("__interrupt__", False)

# if check_interrupt:
#     print("interrupted for human approval")

#     response = agent.invoke(
#         Command( 
#             resume={"decisions": [{"type": "approve"}]}  # or "reject"
#         ),
#         config=config # Same thread ID to resume the paused conversation
#     )

#     # convert response object to dict and print last ai message content
#     last_ai_content = response["messages"][-1].content

#     print(last_ai_content)

# else:
#     print("no interruption, response:")
#     # print ai message response
#     last_ai_content = response["messages"][-1].content
#     print(response)
#     print(last_ai_content)
