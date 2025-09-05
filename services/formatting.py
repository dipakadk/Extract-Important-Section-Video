from typing import List
from datetime import datetime
from llm_models.chat_model_schema import ImportantSection
from get_section import processing_final_result




def time_to_seconds(time_str: str) -> float:
    t = datetime.strptime(time_str, "%H:%M:%S.%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000  # Convert microseconds to seconds






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



def filtering_section(file_name):
    sections= processing_final_result(file_name).sections

    filtered_sections = remove_overlaps(sections)
    return filtered_sections

