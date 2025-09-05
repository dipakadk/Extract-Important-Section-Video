import os
from langchain.prompts import PromptTemplate,ChatPromptTemplate
from llm_models.chat_model_schema import llm,output_parser
import pysrt


def get_text(srt_file_path):
    subtitles = pysrt.open(srt_file_path)
    all_text=""
    for sub in subtitles:
        all_text+=f"{sub.index} - {sub.start} --> {sub.end}\n{sub.text}\n"
    return  all_text
    
    
def generate_topic(file_path):
    template_instruction = """You are an AI assistant that processes subtitles from the video to extract the different topics.
                The subtitle content is provided in the double backticks: ``{srt_content}``.

                **Important Instruction**
                1. Analyze the subtitles and identify the main topics being discussed.
                2. Extract a short title for each topic.
                3. Identify the start timestamp (HH:MM:SS.sssformat) when each topic begins.
                4. Provide a short summary of what is discussed.
                5. Structure the output in JSON format according to this schema: 
                {format_instruction}

                ## Provide the JSON data only. Do not give explaination and steps involved.
                """
    template = ChatPromptTemplate.from_template(template=template_instruction, partial_variables={"format_instruction": output_parser.get_format_instructions()})
    topic_chai = template | llm | output_parser
    result = topic_chai.invoke({"srt_content":get_text(file_path)})
    return result

