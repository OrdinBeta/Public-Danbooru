import os

def make_tags_string(tupled_tags) -> str:
    tag_string = ""
    for tag in tupled_tags:
        tag_string += tag + " "
    return tag_string

def make_dirs(dir_path) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)