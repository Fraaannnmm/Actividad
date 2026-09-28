## Parte A - Conceptual

### Pregunta 1) ¿Qué significa JWT y cuáles son sus tres partes?

JWT significa **JSON Web Token**. Es un token compacto que permite transmitir
información entre partes de forma verificable porque está firmado. Sus tres
partes, separadas por puntos, son:

1. **Header**: contiene metadatos como el tipo (`JWT`) y el algoritmo
   (`HS256`).
2. **Payload**: contiene _claims_ como `sub` (sujeto), `role` (rol) y `exp`
   (expiración). Está codificado en Base64URL, no cifrado.
3. **Signature**: firma el header y el payload con `SECRET_KEY`, permite
   detectar modificaciones.

### Pregunta 2) ¿Por qué el payload NO es seguro para guardar contraseñas?

El payload solo está codificado en Base64URL, por lo que cualquier persona que
obtenga el token puede decodificarlo y leerlo. No debe contener contraseñas,
CVV ni datos médicos. En este proyecto la contraseña solo se almacena como un
hash bcrypt en SQLite y nunca se incluye en el JWT.

### Pregunta 3) ¿Qué sucede si alguien modifica el payload sin conocer `SECRET_KEY`?

La firma original deja de coincidir con el header y el payload alterados.
`python-jose` rechaza el token y FastAPI responde **401 Unauthorized**, por
eso el atacante no puede cambiar su rol a `profesor` de forma válida.

### Pregunta 4) Diferencia entre 401 Unauthorized y 403 Forbidden

- **401 Unauthorized**: la identidad no pudo autenticarse. Se usa cuando falta
  el bearer token, está vencido, fue alterado o las credenciales de `/login`
  son incorrectas. Normalmente se incluye `WWW-Authenticate: Bearer`.

- **403 Forbidden**: la identidad sí fue autenticada, pero no tiene permisos
  suficientes. En esta API, un usuario con rol `estudiante` obtiene 403 al
  solicitar `/admin`.

## Parte B - Práctica

### Estructura:

```text
.
├── auth.py         # bcrypt, JWT y dependencia get_current_user
├── database.py     # SQLite y usuarios demo
├── main.py         # endpoints FastAPI
├── tests/
│   └── test_api.py
├── requirements.txt
└── .env.example
```

### Instalación y ejecución:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Abrir Swagger UI en <http://127.0.0.1:8000/docs>. `/login` recibe
`application/x-www-form-urlencoded` mediante el formulario de Swagger, no JSON.

Usuarios demo:

| Usuario                  | Contraseña      | Rol        |
| ------------------------ | --------------- | ---------- |
| `estudiante@ujap.edu.ve` | `estudiante123` | estudiante |
| `maria@ujap.edu.ve`      | `profesor123`   | profesor   |

### Evidencias Swagger:

Las capturas solicitadas están en [`screenshots/`](./screenshots/):
Todas fueron tomadas en formato horizontal desde Swagger UI, mostrando el
endpoint ejecutado, el código HTTP y el cuerpo de la respuesta.

1. [`01-login-200.png`](./screenshots/01-login-200.png): `POST /login` → 200
   con `access_token`.
2. [`02-privado-200.png`](./screenshots/02-privado-200.png): `GET /privado`
   → 200 con token de estudiante.
3. [`03-admin-403.png`](./screenshots/03-admin-403.png): `GET /admin` → 403
   usando el token de estudiante.

### Verificación:

```bash
pytest -q
```

Resultado esperado: **4 passed**.

> En producción se debe usar una `SECRET_KEY` aleatoria de al menos 32
> caracteres, mantenerla fuera del repositorio y servir la API mediante HTTPS.
