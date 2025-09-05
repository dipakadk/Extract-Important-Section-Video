
import pysrt
from chains import generate_topic,get_imp_section_template
def read_srt(file_path):
    subs = pysrt.open(file_path)
    for sub in subs:
        print(f"{sub.index} - {sub.start} --> {sub.end}\n{sub.text}\n")
    return subs

def subtitle_data(file_name):
    subtitle_data=[]  

    for sub in read_srt(file_name):

        subtitle_data.append({
            "start": sub.start.to_time().strftime("%H:%M:%S.%f")[:-3],
            "end": sub.end.to_time().strftime("%H:%M:%S.%f")[:-3],
            "text": sub.text.replace("\n", " ")  
        })
    return subtitle_data




     
def extract_subtitles_for_topics(subtitles, topics):
    """Matches subtitles with topics based on timestamps."""
    topic_subtitles = {}

    for i, topic in enumerate(topics):


        start_time = topic.start_timestamp
        end_time = topics[i + 1].start_timestamp if i + 1 < len(topics) else "99:99:99"  # End of video
        
        extracted_text = []
        required_srt=[]
        for sub in subtitles:
            if start_time <= sub["start"] < end_time:
                extracted_text.append(sub["text"])
                required_srt.append(sub)

        # Store in dictionary
        topic_subtitles[topic.title]={}
        topic_subtitles[topic.title]["text"] = " ".join(extracted_text)
        topic_subtitles[topic.title]["sections"]=required_srt

    return topic_subtitles



def processing_final_result(file_path):
    topics = generate_topic(file_path).topics

    topic_sentences = extract_subtitles_for_topics(subtitle_data(file_path), topics)

    sample_text=""
    for topic, sentences in topic_sentences.items():
            sample_text+=f"Title: {topic}\nSrt sections: {sentences['sections']}"

    imp_sections_chain=get_imp_section_template(sample_text)

    return imp_sections_chain
