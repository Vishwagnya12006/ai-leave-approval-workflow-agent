import os
from langchain_openai import ChatOpenAI

def visualize_graph(graph_instance, filename: str):
    """Saves a LangGraph object as a Mermaid PNG."""
    print(f"\nSaving graph image to '{filename}'...")
    try:
        with open(filename, "wb") as f:
            f.write(graph_instance.get_graph().draw_mermaid_png())
        print(f"Done! Open {filename} to see the visualization.")
    except Exception as e:
        print(f"Could not generate {filename}: {e}")


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Returns a ChatOpenAI instance pointing to DeepSeek if key is present,
    otherwise falling back to standard OpenAI gpt-4o-mini.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if api_key and "your_deepseek" not in api_key.lower():
        # DeepSeek is OpenAI-compatible, so we use ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            api_key=api_key,
            base_url="https://api.deepseek.com",
            temperature=temperature,
        )
    else:
        # Fallback to OpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
        )
