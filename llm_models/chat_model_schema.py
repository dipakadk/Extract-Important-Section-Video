from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import os


class VideoTopic(BaseModel):
    title: str = Field(..., description="Short title of the topic discussed")
    start_timestamp: str = Field(..., description="Start timestamp of the topic (HH:MM:SS.sss format)")
    text: str = Field(..., description="Short summary or extracted text of the topic")

class VideoTopicsList(BaseModel):
    topics: list[VideoTopic] = Field(..., description="List of extracted topics from the video")

output_parser = PydanticOutputParser(pydantic_object=VideoTopicsList)


class ImportantSection(BaseModel):
    text: str = Field(..., description="A complete important sentence or paragraph spoken in the video .")
    start_timestamp: str = Field(..., description="Start timestamp (HH:MM:SS.sss) when this sentence/paragraph begins.")
    end_timestamp: str = Field(..., description="End timestamp (HH:MM:SS.sss) when this sentence/paragraph ends.")
    
class ImportantSectionsList(BaseModel):
    sections: List[ImportantSection] = Field(..., description="List of most important spoken sentences/paragraphs with timestamps.")
imp_section_finder = PydanticOutputParser(pydantic_object=ImportantSectionsList)


class ChatModelProvider:
    def __init__(self, provider: str = "openai", model: str | None = None):
        if provider not in {"openai", "ollama"}:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        self.provider = provider
        self.model = model

    def create(self):
        if self.provider == "openai":
            from dotenv import load_dotenv
            from langchain_openai import ChatOpenAI

            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Set OPENAI_API_KEY to use the OpenAI LLM.")
            return ChatOpenAI(
                api_key=api_key,
                model=self.model or os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini"),
            )

        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=self.model or os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
