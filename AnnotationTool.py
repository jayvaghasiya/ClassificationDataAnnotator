import streamlit as st
from PIL import Image
import keyboard
import os
import csv
import shutil

cwd = os.getcwd()

st.set_page_config(layout="wide")

out_csv_path = "/home/jay/hdd/dataset/construction_crops.csv"
image_folder = "/home/jay/hdd/dataset/workers"
trash_folder = "/home/jay/hdd/dataset/trash"

st.write("# Multilable Classification Annotator")

# Example configuration
config = [
    {"set_name": "Helment", "num_checkboxes": 3, "names" : ["Absent", "Half_Helmet", "Full_Helmet"]},
    {"set_name": "PPE Kit", "num_checkboxes": 2, "names" : ["Present", "Absent"]},
    {"set_name": "Safety Vest", "num_checkboxes": 2, "names" : ["Present", "Absent", "Unknown"]},
]

labels = ['ImageName', 'Helmet', 'PPEkit', 'SafetyVest']

# Custom SessionState class
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def reload_files():
    print("Reloading files !")
    st.session_state.image_files = sorted([f for f in os.listdir(st.session_state.image_directory) if f.endswith('.jpg') or f.endswith('.png')])

if "output_annotations" not in st.session_state:
    print("Lossing annotated data")
    st.session_state.started = False
    st.session_state.image_index = 0
    st.session_state.output_annotations = {}
    print(st.session_state.output_annotations)

def get_lables():
    image_name = os.path.join(st.session_state.image_directory, st.session_state.image_files[st.session_state.image_index])
    output = []
    for conf in config:
        output.append(st.session_state[f"{conf['set_name']}"])
    st.session_state.output_annotations[image_name] = output

def set_labels():
    print(st.session_state.image_index)
    image_name = os.path.join(st.session_state.image_directory, st.session_state.image_files[st.session_state.image_index])
    if image_name in st.session_state.output_annotations.keys():
        st.session_state.annoatated = True
        old_data = st.session_state.output_annotations[image_name]
        for (conf, selection) in zip(config, old_data):
            st.session_state[conf['set_name']] = selection
    else:
        print("HERE !")
        st.session_state.annoatated = False

def delete_image():
    in_path = os.path.join(st.session_state.image_directory, st.session_state.image_files[st.session_state.image_index])
    out_path = os.path.join(st.session_state.trash_path, st.session_state.image_files[st.session_state.image_index])
    print("Moved to : ", shutil.move(in_path, out_path))

def save_data():
    with open(st.session_state.output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(labels)
        for image_name, values in st.session_state.output_annotations.items():
            row = [image_name] + values
            writer.writerow(row)

def button_click(action):
    if action == "next":
        get_lables()
        if st.session_state.image_index == len(st.session_state.image_files)-1:
            st.balloons()
        else:
            st.session_state.image_index+=1
            set_labels()
    elif action == "back":
        get_lables()
        if st.session_state.image_index == 0:
            st.balloons()
        else: 
            st.session_state.image_index-=1
            set_labels()
    elif action == "not_annotated":
        while True:
            get_lables()
            st.session_state.image_index+=1
            set_labels()
            if st.session_state.image_index == len(st.session_state.image_files)-1:
                st.balloons()
                break
            if st.session_state.annoatated:
                continue
    elif action == "delete":
        delete_image()
        reload_files()
    elif action == "save":
        get_lables()
    save_data()


def create_checkboxes():
    session_state = SessionState()

    num_columns = 3
    column_sets_config=[[], [], []]
    columns = [col1, col2, col3] = st.columns([1,1,1])
    sets_per_column = len(config) // num_columns

    conf_index = 0
    for conf in range(len(config)):
        if conf_index == num_columns:
            conf_index = 0
        column_sets_config[conf_index].append(config[conf])
        conf_index+=1

    for index, set_config in enumerate(column_sets_config):
        set_name = set_config[0]["set_name"]
        num_checkboxes = set_config[0]["num_checkboxes"]
        names = set_config[0]["names"]

        with columns[index]:
            set_state = st.radio(set_name, names, key=set_name)
            st.session_state.set_name = set_state


def on_click_st_button():
    if not st.session_state.started:
        reload_files()
    st.session_state.started = not st.session_state.started
    if "annotated" not in st.session_state:
        set_labels()


def reload_old_annotations():
    with open(st.session_state.output_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            image_name = row[0]
            values = row[1:]
            st.session_state.output_annotations[image_name] = values
    print("completed reload !")
    # print(st.session_state.output_annotations)


def resize_image(image, new_height=400):
    # Calculate the new width based on the desired height and aspect ratio
    aspect_ratio = image.width / image.height
    new_width = int(new_height * aspect_ratio)

    # Resize the image while maintaining the aspect ratio
    resized_image = image.resize((new_width, new_height))

    # Return the resized image
    return resized_image


def get_image():
    img = Image.open(os.path.join(st.session_state.image_directory, st.session_state.image_files[st.session_state.image_index]))
    if img.size[-1] > 400:
        img = resize_image(img)
    return img


def main():
    c1, c2, _, c3, c4, c5 = st.columns(6)
    with c1:
        st.text_input("Select Annotation File ", key="output_file", value=out_csv_path)
    with c2:
        st.write("")
        st.write("")
        st.button("Reload", on_click=reload_old_annotations)
    with c3:
        st.text_input("Images Folder Path ", value=image_folder, key="image_directory")
    with c4:
        st.text_input("Trash Folder Path ", value=trash_folder, key="trash_path")
    with c5:
        st.write("")
        st.write("")
        st.button("Start" if not st.session_state.started else "Stop", on_click=on_click_st_button)

    st.write("-"*5)

    if st.session_state.started:
        col1, col2 = st.columns(2)
        with col2:
            col21, col22, col221, col23, col24 = col2.columns([1,1,1.5,1,1])
            with col21:
                st.button('Back', on_click=button_click, args=("back",))
            with col22:
                st.button('Next', on_click=button_click, args=("next",))
            with col221:
                st.button('Next Not Annotated', on_click=button_click, args=("not_annotated",))
            with col23:
                st.button('Delete', on_click=button_click, args=("delete",))
            with col24:
                st.button('Save', on_click=button_click, args=("save",))
            st.write("-"*5)
            create_checkboxes()

        with col1:
            col11, col12, col13 = col1.columns([0.01, 1, 0.2])
            with col12:
                if st.session_state.annoatated:
                    st.write(":blue[{}/{}]  : {}    :: :green[Already Annotated]".format(st.session_state.image_index, len(st.session_state.image_files)-1, st.session_state.image_files[st.session_state.image_index]))
                else:
                    st.write(":blue[{}/{}]  : {}    :: :red[Not Annotated]".format(st.session_state.image_index, len(st.session_state.image_files)-1, st.session_state.image_files[st.session_state.image_index]))
                st.image(get_image())

# Run the main function
if __name__ == '__main__':
    main()