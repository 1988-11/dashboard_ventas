import streamlit_authenticator as stauth

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

# Generar hashes
hashed_passwords = stauth.Hasher(passwords).generate()

# Mostrar los hashes
for i, h in enumerate(hashed_passwords):
    print(f"{passwords[i]} → {h}")