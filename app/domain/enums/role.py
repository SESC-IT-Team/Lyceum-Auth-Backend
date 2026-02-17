from enum import Enum


class Role(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    staff = "staff"
