from typing import List
from llm_models.chat_model_schema import ChatModelProvider, ImportantSection
from services.get_section import processing_final_result
from services.timestamp_validation import timestamp_to_milliseconds
from chains.quality_control_chain import QualityControlAgent




def time_to_seconds(time_str: str) -> float:
    return timestamp_to_milliseconds(time_str) / 1000


def remove_overlaps(sections: List[ImportantSection]) -> List[ImportantSection]:
    sections = sorted(sections, key=lambda sec: time_to_seconds(sec.start_timestamp))

    filtered_sections = []
    prev_end_time = 0

    for sec in sections:
        start_time = time_to_seconds(sec.start_timestamp)
        end_time = time_to_seconds(sec.end_timestamp)

        if start_time >= prev_end_time:
            filtered_sections.append(sec)
            prev_end_time = end_time 

    return filtered_sections



def filtering_section(file_name, llm_provider="openai", ollama_model=None, video_duration=None):
    llm = ChatModelProvider(provider=llm_provider, model=ollama_model).create()
    sections = processing_final_result(file_name, llm_provider, ollama_model, llm=llm).sections

    sections = QualityControlAgent().run(sections, file_name, video_duration, llm)
    filtered_sections = remove_overlaps(sections)
    return filtered_sections

