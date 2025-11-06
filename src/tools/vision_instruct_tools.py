# --- imports unchanged ---
import base64, json
from pathlib import Path
from types import SimpleNamespace

from wayflowcore.agent import Agent
from wayflowcore.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

from src.llm.oci_genai_vision import initialize_llm_vision

from src.data.sales_order import Transaction as data_structure

# ---------- helpers ----------

def _encode_image_as_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ---------- tool wrapper ----------
@tool(description_mode="only_docstring")
def image_to_text(file_path: str, question: str) -> str:
    """
    a tool to convert image to text
    :param image_file_path:
    :param question:
    :return: JSON string extracted from the image as per schema
    """
    return image_to_text_impl(file_path, question)

def image_to_text_impl(file_path: str, question: str) -> str:
    """Plain callable that actually does the work."""
    image_base64 = _encode_image_as_base64(file_path)
    data_schema_str = json.dumps(data_structure.model_json_schema(), indent=2)

    messages = [
        SystemMessage(
            content=(
                "You are a helpful assistant. Use the schema below to extract structured JSON from the user's request.\n"
                "Respond with valid JSON inside triple backticks like ```json ... ```.\n\n"
                f"Schema:\n```json\n{data_schema_str}\n```\n"
                "Return only the final JSON block, and nothing else."
            )
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            ]
        ),
    ]
    llm = initialize_llm_vision()
    resp = llm.invoke(messages)
    return resp.content

# ---------- test / demo ----------
def test():
    from src.llm.oci_genai import initialize_llm
    base_llm = initialize_llm()

    assistant = Agent(
        custom_instruction="Get information from the file",
        tools=[image_to_text],
        llm=base_llm,
    )

    THIS_DIR = Path(__file__).resolve()
    PROJECT_ROOT = THIS_DIR.parent.parent.parent
    file_path = f"{PROJECT_ROOT}/order_inputs/orderhub_handwritten.jpg"
    question = (
        "Extract all order information with this schema:\n"
        "BillToCustomer - Name, BusinessUnit \n"
        "OrderItems - Item: {}, Quantity: {}, RequestedDate: {}\n"
        "Return only JSON."
    )

    # Deterministic, direct
    # print(image_to_text_impl(file_path=file_path, question=question))

    print("+++++++++++++++ \n\n")
    # Wayflow conversation path - Non Deterministic Testing
    convo = assistant.start_conversation()
    # Provide input in a form your template can key on
    user_msg = f"file_path: {file_path}\nquestion: {question}"
    convo.append_user_message(user_msg)
    convo.execute()

    ans = convo.get_last_message()
    print(ans.content)


if __name__ == "__main__":
    test()