import mysql.connector
import face_recognition
import cv2
import numpy as np
import os
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="123456",
  database="attendance"
)

mycursor = mydb.cursor()

d={"unknown":0,"ram":1,"elon musk":2,"devesh":3,"joe biden":4}
u_id=1
kn_encodings=[]
known_face_names =[]
present=[]
cont=0
mycursor.execute("SELECT * FROM STUDENTS")
p=mycursor.fetchall()
print(p)

mycursor.execute("TRUNCATE ATTENDANCE")
mydb.commit()
print("emptied table")

video_capture = cv2.VideoCapture(0)

for i in p:
    if i[1].lower()!="unknown":
        person_image=face_recognition.load_image_file(i[2])
        en=face_recognition.face_encodings(person_image)[0]
        kn_encodings.append(en)
        known_face_names .append(i[1])
    else:
        pass

print(known_face_names )



# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(kn_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in kn_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(kn_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            if name not in present and name.lower() !="Unknown":
                present.append(name)
                k="'"+name.upper()+"'"
                com="INSERT INTO ATTENDANCE(ID,NAME,DATE_TIME,PATH) VALUES({},{},NOW(),NULL)".format(d[name.lower()],k)
                mycursor.execute(com)
                mydb.commit()
                cont=0
                print(com)
            elif name.lower()=="unknown" and cont==0:
                n="unknown_{}.jpg".format(u_id)
                path = "'"+str(os.getcwd()) + "\\" + n+"'"
                ty="'"+name.upper()+"_"+str(u_id)+"'"
                path=path.replace("\\","/")
                print(path,ty,n)
                u_id+=1
                cont+=1
                com = "INSERT INTO ATTENDANCE(ID,NAME,DATE_TIME,PATH) VALUES({},{},NOW(),{})".format(d[name.lower()], ty, path)
                mycursor.execute(com)
                mydb.commit()
                print(com)
                cv2.imwrite(n,frame)
            # print(present)
    process_this_frame = not process_this_frame

    # Display the results

    for (up, s1, down, s2), name in zip(face_locations, face_names):
        up *= 4
        s1 *= 4
        down *= 4
        s2 *= 4

        cv2.rectangle(frame, (s2, up), (s1, down), (255, 255, 255), 2)
        cv2.rectangle(frame, (s2, up - 35), (s1, up), (255, 255, 255), cv2.FILLED)
        cv2.putText(frame, name, (s2 + 6, up - 6), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    # Display the resulting image
    cv2.imshow('Video', frame)


    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()




