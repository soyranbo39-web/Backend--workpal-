from .Alumnos import Alumno
from .Proyecto_Alumnos import ProyectoAlumno
from .Proyectos import Proyecto
from .Users import User

Autor = User
Proyecto_Alumno = ProyectoAlumno

__all__ = [
    "User",
    "Autor",
    "Alumno",
    "ProyectoAlumno",
    "Proyecto_Alumno",
    "Proyecto"
]

