from enum import Enum


class Role(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"
    staff = "staff"
    guest = "guest"
    graduate = "graduate"
