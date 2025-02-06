import sys
from flask import Flask, request, json
import face_recognition
from flask_cors import CORS
import cv2
import numpy
import subprocess
from PIL import Image
import imageio

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/compare-face", methods=["POST"])
def compareface():
    ok = "false"
    message = ""
    # print("compate face", file=sys.stderr)
    data = json.loads(request.data)
    print(data, file=sys.stderr)
    image1 = data["image1"]
    image2 = data["image2"]

    try:
        known_image = face_recognition.load_image_file(image1)
        unknown_image = face_recognition.load_image_file(image2)

        biden_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

        results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        ok = results[0]
    except IndexError:
        ok = "False"
        message = "Eomparison error on images"
    except FileNotFoundError:
        ok = "False"
        message = "Image not found"

    return {"compare": str(ok), "message": message}


@app.route("/validate-selfie-video-cv", methods=["POST"])
def validateSelfieVideoCv():
    ok = "False"
    message = ""
    data = json.loads(request.data)
    print(data, file=sys.stderr)

    frame_number = 0
    success_validations = 0
    try:
        # Open the input movie file
        input_movie = cv2.VideoCapture(data["selfiePath"])
        # length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create an output movie file (make sure resolution/frame rate matches input video!)
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # output_movie = cv2.VideoWriter('output.avi', fourcc, 29.97, (640, 360))

        # Load some sample pictures and learn how to recognize them.
        lmm_image = face_recognition.load_image_file(data["image1"])
        lmm_face_encoding = face_recognition.face_encodings(lmm_image)[0]

        al_image = face_recognition.load_image_file(data["image2"])
        al_face_encoding = face_recognition.face_encodings(al_image)[0]

        known_faces = [lmm_face_encoding, al_face_encoding]

        # Initialize some variables
        face_locations = []
        face_encodings = []

        while True:
            # Grab a single frame of video
            ret, frame = input_movie.read()
            frame_number += 1
            # print('frame_number',  file=sys.stderr)
            # print(frame_number,  file=sys.stderr)

            # Quit when the input video file ends
            if not ret:
                break

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_frame = numpy.ascontiguousarray(frame[:, :, ::-1])
            # frame[:, :, ::-1]
            # print('loading frames',  file=sys.stderr)

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_frame)
            # print('face_locations loaded',  file=sys.stderr)

            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # print('face encoding loaded',  file=sys.stderr)

            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces(
                    known_faces, face_encoding, tolerance=0.50
                )
                # print('match ' + str(success_validations),  file=sys.stderr)
                # print(match,  file=sys.stderr)

                if match[0]:
                    ok = "True"
                elif match[1]:
                    ok = "True"

            # print(ok + str(success_validations), file=sys.stderr)
            if ok == "True":
                # print('success',  file=sys.stderr)
                success_validations += 1

            if success_validations >= 10:
                break

        message = "detection completed for all frames - " + str(frame_number)

    except IndexError:
        if frame_number == 0:
            ok = "False"
            message = "Face detection error occured in video"
        else:
            message = "detection completed - " + str(frame_number)

    print(message + " " + ok, file=sys.stderr)
    # All done!
    input_movie.release()
    cv2.destroyAllWindows()

    return {"ok": str(ok), "message": str(message)}


@app.route("/convert-to-mp4", methods=["POST"])
def convertToMp4():
    ok = "false"
    message = ""
    data = json.loads(request.data)
    print(data, file=sys.stderr)

    try:
        # ffmpeg.input(data["input_file_path"]).output(data["output_file_path"]).run()
        # ffmpeg = (
        # FFmpeg().option("y").input(data["input_file_path"]).output(
        #    data["output_file_path"],
        #   codec="copy",
        #    )
        # )

        # @ffmpeg.on("progress")
        # def on_progress(progress: Progress):
        #    print(progress)

        # await ffmpeg.execute()
        input_file_path = data["input_file_path"]  # path to input file
        output_file_path = data["output_file_path"]  # path to output file

        # FFmpeg command to convert the input file to an MP4 file
        command = [
            "ffmpeg",
            "-i",
            input_file_path,
            "-f",
            "mp4",
            "-vcodec",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "22",
            output_file_path,
        ]

        #  Run the FFmpeg command
        subprocess.run(command)
        ok = "True"
        message = "success"

    except FileNotFoundError:
        ok = "False"
        message = "Video not found"
        print("File not found", file=sys.stderr)

    return {"ok": str(ok), "message": str(message)}



@app.route("/validate-selfie-video", methods=["POST"])
def validateSelfieVideo():
    ok = "False"
    message = ""
    data = json.loads(request.data)
    print(data, file=sys.stderr)

    frame_number = 0
    success_validations = 0
    try:
        # Open the video file using imageio
        video_reader = imageio.get_reader(data["selfiePath"])
       
        lmm_image = face_recognition.load_image_file(data["image1"])
        lmm_face_encoding = face_recognition.face_encodings(lmm_image)[0]

        #al_image = face_recognition.load_image_file(data["image2"])
        #al_face_encoding = face_recognition.face_encodings(al_image)[0]

        known_faces = [lmm_face_encoding, ]#al_face_encoding

        # Initialize some variables
        face_locations = []
        face_encodings = []

        # Iterate through each frame of the video
        for frame in video_reader:
            # Convert the frame to a Pillow Image object
            image = Image.fromarray(frame)
            frame_number +=1
            # Do something with the image, such as display it or save it to a file
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(frame)
            # print('face_locations loaded',  file=sys.stderr)

            face_encodings = face_recognition.face_encodings(frame, face_locations)

            print('face encoding loaded',  file=sys.stderr)

            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces(
                    known_faces, face_encoding, tolerance=0.50
                )
                # print('match ' + str(success_validations),  file=sys.stderr)
                # print(match,  file=sys.stderr)

                if match[0]:
                    ok = "True"
                elif match[1]:
                    ok = "True"
                
            # Release the memory used by the frame
            del frame   
                
            print(ok + str(success_validations), file=sys.stderr)
            if ok == "True":
                # print('success',  file=sys.stderr)
                success_validations += 1

            if success_validations >= 5:
                break    
            
        print(ok + str(success_validations), file=sys.stderr)
        message = "detection completed for all frames - " + str(frame_number)

    except IndexError:
        if frame_number == 0:
            ok = "False"
            message = "Face detection error occured in video"
        else:
            message = "detection completed - " + str(frame_number)

    print(message + " " + ok, file=sys.stderr)
    

    return {"ok": str(ok), "message": str(message)}



if __name__ == "__main__":
    app.run("localhost", 6969)
