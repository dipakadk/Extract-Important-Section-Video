from langchain.prompts import PromptTemplate
from llm_models.chat_model_schema import imp_section_finder
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
import os
llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'),model='gpt-4o-mini',stream_usage=True)


def get_imp_section_template(processed_text):
    template_ins = """
    You are an AI assistant that processes video subtitles and extracts the **most important spoken sentences/paragraphs** while ensuring their timestamps are **accurate**.

    **Instructions:**
    1. Analyze the subtitle text and **identify the most meaningful and relevant** sentences or short paragraphs.
    2. The extracted text should be **self-contained**, ensuring the meaning is preserved.
    3. **Ensure accurate timestamps** by selecting complete sentences/paragraphs.
    4. Return the result in the following structured JSON format:
    {format_instructions}

    **Here is the subtitle content:**
    {srt_content}
    **Now extract the most important spoken sentences/paragraphs with their timestamps.**

    # Double verify time-stamps. Check timestamp very properly and include the same as provided in srt content. 
    """

    temp = PromptTemplate.from_template(
        template=template_ins,
        partial_variables={"format_instructions": imp_section_finder.get_format_instructions()}
    )

    imp_sec_finder_chain = temp | llm | imp_section_finder

    imp_sec_result = imp_sec_finder_chain.invoke({"srt_content": processed_text})

    return imp_sec_result

