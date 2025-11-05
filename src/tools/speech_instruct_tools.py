# Convert Voice to Text
from wayflowcore.agent import Agent
from wayflowcore.tools import tool

# ---------- tool wrapper ----------
@tool(description_mode="only_docstring")
def voice_to_text(file_path: str, question: str) -> str:
    """
    a tool to convert voice to text
    :param voice_file_path:
    :param question:
    :return: JSON string extracted from the voice as per schema
    """
    return voice_to_text_impl(file_path, question)

def voice_to_text_impl(file_path: str, question: str) -> str:
	return ""