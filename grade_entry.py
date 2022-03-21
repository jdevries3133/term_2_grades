"""Script for grade entry into oncourse"""

import csv
from typing import cast
from time import sleep

import pyautogui as pg
from teacherhelper import Helper


code_to_teacher = {
    "7A": "Espiritu, Melissa",
    "6E": "Shuzman, Adam",
    "7B": "Davis, Shondell",
    "7E": "Baurkot, Juliana",
    "7C": "Zhu, Zhu",
    "7D": "Regan, Katelyn",
    "6C": "Zou, Jiying",
    "6D": "Chung, Soyoun",
    "5D": "Silvestri, Melissa",
    "6A": "Irizarry, Gina",
    "6B": "Saadeh, Salwa",
    "5C": "Armstead, Joseph",
    "5B": "Geltzeiler, Katelyn",
    "5A": "Kassalow, Anne",
    "4B": "DuVal, Dina",
    "5E": "Ruffee, Michele",
    "4E": "Carrie, Jannine",
    "4C": "Morrow, Lisa",
    "4E": "Chartier, Jessica",
    "4D": "Rodriguez, Joseph",
    "4A": "McNeill, Kaity",
}

helper = cast(Helper, Helper.read_cache())

with open("./output_fifth.csv", "r") as fp:
    rd = csv.DictReader(fp)
    for row in rd:
        st = helper.find_nearest_match(name := row["name"])
        if st is None:
            raise Exception(f"cannot match name: {name}")
        st.project_grade = row["total"]  # type: ignore


while True:
    current = input("enter current homeroom: ").upper()
    if current not in code_to_teacher:
        raise ValueError("unacceptable homeroom code")

    hr = helper.homerooms[code_to_teacher[current]]

    students = sorted(hr.students, key=lambda s: s.last_name)

    print("focus first text box now!!")
    for i in range(5, 0, -1):
        print(i)
        sleep(0.5)
    for s in students:
        if (grade := getattr(s, "project_grade")) is not None:
            pg.typewrite(grade)
        pg.press("down")
