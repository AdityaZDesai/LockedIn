import os
from flask import Flask
from flask import render_template, request, redirect, url_for
from openai import OpenAI
import json


app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.static_folder, 'input')
@app.route("/main")
def main():
    return "<h1> HELLLOOO </h1>"

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        uploaded_file = request.files['filename']
        if uploaded_file.filename != '':
            filepath = os.path.join(UPLOAD_FOLDER, "lecture.mp4")
            uploaded_file.save(filepath)
            audiosplitter()
            topic = open("static/transcripts/topic.txt", "r").read()
            generate_quiz_question(topic)
    return render_template('upload.html')

@app.route("/", methods=['GET', 'POST'])
def upload_file():
    return redirect(url_for('main'))

@app.route("/watch", methods=['GET'])
def watch():
    videos_folder = os.path.join(app.static_folder, 'videos')
    videos = [f for f in os.listdir(videos_folder) if f.endswith('.mp4')]
    return render_template('watch.html', videos=videos, len= len(videos))

@app.route("/submit", methods=['POST', 'GET'])
def submit():
    f = open('static/transcripts/quiz.json')
    quiz_data = json.load(f)
    score = 0
    correct_answers = []
    user_answers = request.form
    print(user_answers)
    for idx, qa in enumerate(quiz_data['questionsandanswers']):
        if user_answers.get(f'{qa['category']}') == qa['answers'][qa['correct']]:
            score += 1
            correct_answers.append(True)
        else:
            correct_answers.append(False)
    return render_template('result.html', score=score, total=len(quiz_data['questionsandanswers']), quiz=quiz_data, yourans= user_answers.get(f'{qa['category']}'))



@app.route("/quiz", methods=['POST', 'GET'])
def quiz():
    f = open('static/transcripts/quiz.json')
    data = json.load(f)
    print(data['questionsandanswers'])
    return render_template('quiz.html', quiz=data)




def generate_quiz_question(summary):
    client = OpenAI(
        api_key="<API KEY FIRST>"
    )


    functions = [
        {
            "name": "get_question",
            "description": "Get the multiple choice question related to the exerpt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "questionsandanswers": {
                        "type": "array",
                        "description": "an array representing the questions and answers related to exerpt.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "A word describing the category of the question"
                                },
                                "question": {
                                    "type": "string",
                                    "description": "A question relating to the exerpt."
                                },
                                "answers":{
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "description": "An answer option"
                                    }
                                },
                                "correct":{
                                    "type": "integer",
                                    "description": "The index number of the correct answer for the answers provided."
                                }
                            }
                        }
                    }
                }
            },
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are responding to email from a business client and your text output will be sent directly to them in full unedited. "
                        "They cannot not know in anyway that you are a generative AI or chatbot of any kind. "
                        "Provide FIVE multiple choice question for the following exerpt. For each question, also specify the category of the question."
                        "It must have four options, and the correct option must have an exclamation mark at the end of its sentence."
                    )
                },
                {"role": "user", "content": summary},

            ],
            functions=functions,
            function_call={
                "name": "get_question",
            }
        )
        # Loading the response as a JSON object
        file_path = open("static/transcripts/quiz.json", 'w')
        file_path.write(response.choices[0].message.function_call.arguments)
        json_response = json.loads(response.choices[0].message.function_call.arguments)
        print(json_response)
        return response.choices[0].message
    except Exception as e:
        print(e)
        return None

#topic = open("static/transcripts/topic.txt", "r").read()
#print(topic.read())









import ctypes
from http import client
import io
import json
import re
import sys
import openai
from openai import OpenAI
import moviepy.editor as mp
from pydub import AudioSegment
import os
import subprocess
openai.api_key = "<API KEY FIRST>"



# with open("harvard.wav", "rb") as audio_file:
#     transcript2 = openai.Audio.transcribe(
#         file = audio_file,
#         model = "whisper-1",
#         response_format="srt",
#         language="en"
#     )
# print(transcript2)

# output_json_path = "transcription_result.json"
# with open(output_json_path, "w") as json_file:
#     json.dump(transcript2, json_file, indent=4)


# # function that takes in string argument as parameter 
# def comp(PROMPT, MaxToken=50, outputs=3): 
#     # using OpenAI's Completion module that helps execute  
#     # any tasks involving text  
#     response = openai.Completion.create( 
#         # model name used here is text-davinci-003 
#         # there are many other models available under the  
#         # umbrella of GPT-3 
#         model="text-davinci-003", 
#         # passing the user input  
#         prompt=PROMPT, 
#         # generated output can have "max_tokens" number of tokens  
#         max_tokens=MaxToken, 
#         # number of outputs generated in one call 
#         n=outputs,
#         type="json_file",
#     ) 
#     # creating a list to store all the outputs 
#     output = list() 
#     for k in response['choices']: 
#         output.append(k['text'].strip()) 
#     return output

# PROMPT = """Write a story to inspire greatness, take the antagonist as a Rabbit and protagnist as turtle.  
# Let antagonist and protagnist compete against each other for a common goal.  
# Story should atmost have 3 lines."""
# comp(PROMPT, MaxToken=3000, outputs=3)


# # def upload_file(file_path):
    
# 	# Upload a file with an "assistants" purpose
# 	file_to_upload = client.files.create(
#   	file=open(file_path, "rb"),
#   	purpose='assistants'
# 	)
# 	return file_to_upload
 
# transformer_paper_path = "./transcription_result.json"
# file_to_upload = upload_file(transformer_paper_path)

# def create_assistant(assistant_name,
#                  	my_instruction,
#                  	uploaded_file,
#                  	model="gpt-4-1106-preview"):
    
# 	my_assistant = client.beta.assistants.create(
# 	name = assistant_name,
# 	instructions = my_instruction,
# 	model="gpt-4-1106-preview",
# 	tools=[{"type": "retrieval"}],
# 	file_ids=[uploaded_file.id]
# 	)
    
# 	return my_assistant

# inst="You are a polite and expert knowledge retrieval assistant. Use the documents provided as a knowledge base to answer questions"
# assistant_name="Scientific Paper Assistant"

# my_assistant = create_assistant(assistant_name, inst, file_to_upload)





from openai import OpenAI
import pydub


# Set the path to ffmpeg and ffprobe
AudioSegment.converter = os.getcwd()+ "\\ffmpeg.exe"                    
# AudioSegment.ffprobe   = os.getcwd()+ "\\ffprobe.exe"
# sound = pydub.AudioSegment.from_mp3(os.getcwd()+"\\sample.mp3")


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<THE OTHER ONE>"))

# ctypes.windll.user32.MessageBoxW(0, "Transcription completed successfully!", "Notification", 1)

def audiosplitter():

    # clip = mp.VideoFileClip("static/input/lecture.mp4")
    # clip.audio.write_audiofile("testaudio.mp3")

    # clip = AudioSegment.from_mp3("testaudio.mp3")
    # ten_minutes = 10 * 60 * 1000
    # first_ten_minutes = clip[:ten_minutes]
    # first_ten_minutes.export("testaudio.mp3", format="mp3")

    # audio_file = open("testaudio.mp3", "rb")
    # transcript = client.audio.transcriptions.create(
    # file=audio_file,
    # model="whisper-1",
    # response_format="verbose_json",
    # timestamp_granularities=["segment"]
    # )

    # # Convert the transcript object to a dictionary
    # data = transcript.to_dict()

    # # Write the dictionary to a JSON file
    # with open("transcript.json", "w") as json_file:
    #     json.dump(data, json_file, indent=4)
    #     newFile = open("static/transcripts/topic.txt", "w")
    #     newFile.write(data['text'])
        



    # def show_json(obj):
    #     print(json.loads(obj.model_dump_json()))

    # file = client.files.create(
    # file=open("transcript.json", "rb"),
    # purpose='assistants'
    # )

    # assistant = client.beta.assistants.create(
    #     name="LockInBot",
    #     instructions="You are an artificial intelligence lecturer that will receive a transcription of a lecture in json format, with timestamps of the things being said. You must return the timestamps where the important parts of the lecture are being said. Please provide timestamps of 3 important parts of the lecture, each part should be around 1 minute long, and you are allowed to combine different sections of timestamps into one whole part if the lecturer is explaining the same concept. You should give the start and end points of the timestamp. Also give a brief summary of what each part is talking about. The format has to be Part 1: [start, end] \n Summary of what is being said. \n Part 2: [start, end] \n Summary of what is being said. \n Part 3: [start, end] \n Summary of what is being said. Do not deter from this format.",
    #     model="gpt-4o-mini",
    #     tools=[{"type": "code_interpreter"}],
    #     tool_resources={
    #         "code_interpreter": {
    #         "file_ids": [file.id]
    #         }
    #     }
    # )
    # show_json(assistant)

    # thread = client.beta.threads.create(
    # messages=[
    #     {
    #     "role": "user",
    #     "content": "Lecture transcriptions uploaded.",
    #     "attachments": [
    #         {
    #         "file_id": file.id,
    #         "tools": [{"type": "code_interpreter"}]
    #         }
    #     ]
    #     }
    # ]
    # )

    # # message = client.beta.threads.messages.create(
    # #     thread_id=thread.id,
    # #     role="user",
    # #     content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
    # # )
    # # show_json(thread)



    # run = client.beta.threads.runs.create(
    #     thread_id=thread.id,
    #     assistant_id=assistant.id,
    # )
    # # show_json(run)



    # # def pretty_print(messages):
    # #     print("# Messages")
    # #     for m in messages:
    # #         print(f"{m.role}: {m.content[0].text.value}")
    # #     print()

    # def pretty_print(messages):
    #     output = "# Messages\n"
    #     for m in messages:
    #         output += f"{m.role}: {m.content[0].text.value}\n"
    #     output += "\n"
    #     return output



    # import time

    # def wait_on_run(run, thread):
    #     while run.status == "queued" or run.status == "in_progress":
    #         run = client.beta.threads.runs.retrieve(
    #             thread_id=thread.id,
    #             run_id=run.id,
    #         )
    #         time.sleep(0.5)
    #     return run
    # run = wait_on_run(run, thread)
    # # show_json(run)



    # messages = client.beta.threads.messages.list(thread_id=thread.id)
    # show_json(messages)

    # # def submit_message(assistant_id, thread, user_message):
    # #     client.beta.threads.messages.create(
    # #         thread_id=thread.id, role="user", content=user_message
    # #     )
    # #     return client.beta.threads.runs.create(
    # #         thread_id=thread.id,
    # #         assistant_id=assistant_id,
    # #     )

    # # def get_response(thread):
    # #     return client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    
    
    # # pretty_print(get_response(thread))


    # # input_text = pretty_print(get_response(thread))

    # # print("Captured input_text:")
    # # print(input_text)



    # def submit_message(assistant_id, thread, user_message):
    #     client.beta.threads.messages.create(
    #         thread_id=thread.id, role="user", content=user_message
    #     )

    # # Save the output of pretty_print to a file
    # formatted_messages = pretty_print(messages)
    # with open("messages_output.txt", "w") as file:
    #     file.write(formatted_messages)

    # Read the file content to use it as input_text
    with open("messages_output.txt", "r") as file:
        input_text = file.read()

    print("Captured input_text:")
    print(input_text)
    # Now you can use input_text
    timestamps = re.findall(r'[(\d+.\d+): (\d+.\d+)]', input_text)
    print(timestamps)






    # Function to convert timestamp to seconds
    def timestamp_to_seconds(timestamp):
       return float(timestamp)

    # Extract timestamps using regex
    timestamp = re.findall(r'[(\d+.\d+): (\d+.\d+)]', input_text)    
    
    # Convert timestamps to seconds
    timestamps_in_seconds = [(timestamp_to_seconds(start), timestamp_to_seconds(end)) for start, end in timestamp]

    # Generate ffmpeg commands
    def generate_ffmpeg_commands(timestamps, input_video, output_folder):
        commands = []
        for i, (start, end) in enumerate(timestamps):
            output_video = f"{output_folder}/part{i+1}.mp4"
            command = [
                'ffmpeg', '-i', input_video,
                '-ss', str(start), '-to', str(end),
                '-c', 'copy', output_video
            ]
            commands.append(command)
        return commands

    # Run ffmpeg commands
    def run_ffmpeg_commands(commands):
        for command in commands:
            subprocess.run(command)

    # Example usage
    input_video = 'static/input/lecture.mp4'
    output_folder = 'static/videos'
    commands = generate_ffmpeg_commands(timestamps_in_seconds, input_video, output_folder)
    run_ffmpeg_commands(commands)









if __name__ == "__main__":
    app.run(debug=True)
