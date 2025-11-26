import bcrypt

# Lista de contraseñas originales
passwords = [
    "guillermo1",
    "maria2025",
    "yeseniaf2025",
    "jara2025",
    "jorgechavez1",
    "josec2025",
    "milena2025",
    "oficina2025",
    "admin123"
]

# Generar y mostrar hashes
for pwd in passwords:
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    print(f"{pwd} → {hashed.decode()}")