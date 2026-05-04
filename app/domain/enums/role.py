from enum import Enum


class RoleType(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"
    staff = "staff"
    guest = "guest"
    graduate = "graduate"
