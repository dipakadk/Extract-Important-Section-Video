import os
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()


llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),model="gpt-4o-mini")


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
