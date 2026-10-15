# EcoHarmony Park

Aplicacion web responsive para EcoHarmony Park.

## Estructura

```text
tp06/
├── app/
│   ├── main.py                         # punto de entrada de FastAPI
│   ├── dominio/                        # reglas del negocio
│   │   └── servicios/
│   │       └── reglas_compra.py        # validaciones de la user story
│   ├── aplicacion/                     # acciones completas del sistema
│   │   └── casos_de_uso/
│   │       └── comprar_entradas.py    # coordina el proceso de compra
│   ├── infraestructura/               # detalles tecnicos externos
│   │   ├── base_de_datos/              # persistencia de compras y usuarios
│   │   ├── pagos/                      # Mercado Pago simulado
│   │   └── notificaciones/             # correo SMTP con Gmail
│   └── interfaces/                     # entrada y salida de la aplicacion
│       ├── estaticos/                  # CSS, JavaScript e imagenes
│       ├── plantillas/                 # HTML, Jinja2 y HTMX
│       └── rutas/                      # rutas de FastAPI
└── tests/
    └── unitarias/                    # pruebas unitarias de TDD
```

La carpeta `dominio` no conoce FastAPI ni la base de datos. La carpeta
`aplicacion` coordina los casos de uso y `interfaces` se ocupa del frontend
y de las rutas web.


Las pruebas se encuentran en `tests/unitarias/test_compra.py`.
La implementación de las reglas se encuentra en `app/dominio/servicios/reglas_compra.py`.
El caso de uso completo se encuentra en `app/aplicacion/casos_de_uso/comprar_entradas.py`.

## Responsabilidades de cada archivo

Los archivos principales participan en el proceso de compra con distintas
responsabilidades:

```text
compras.py
    Controller o router de FastAPI.
    Recibe la solicitud HTTP y devuelve una respuesta HTTP.

comprar_entradas.py
    Caso de uso.
    Coordina el proceso completo de compra.

reglas_compra.py
    Dominio.
    Contiene las reglas de negocio y las validaciones de la compra.
```

El recorrido esperado es:

```text
Formulario web
    -> compras.py
    -> comprar_entradas.py
    -> reglas_compra.py
    -> resultado de la compra
    -> respuesta web
```

`compras.py` no debe contener las reglas de negocio. Su responsabilidad es
recibir datos y mostrar resultados; las validaciones se realizan en el dominio
a traves del caso de uso.

## Configuracion del proyecto

Los siguientes comandos deben ejecutarse desde la carpeta raiz del proyecto,
la carpeta que contiene `requirements.txt`.

### 1. Crear un entorno virtual

En Windows usando PowerShell:

```powershell
py -m venv .venv
```

### 2. Activar el entorno virtual

```powershell
.venv\Scripts\Activate.ps1
```

Si PowerShell no permite activar el entorno, se puede ejecutar el interprete
del entorno directamente usando `.venv\Scripts\python.exe`.

### 3. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

La opcion `-r` indica que pip debe leer e instalar todas las librerias
enumeradas en `requirements.txt`.

### 4. Configurar los correos con Gmail

Desde la carpeta `tp06`, copiar el ejemplo (si ya existe `app/.env`, completar
ese archivo conservando su contenido):

```powershell
Copy-Item app/.env.example app/.env
```

En `app/.env`, completar `SMTP_USER` con la cuenta Gmail que enviara los correos
y `SMTP_PASSWORD` con su **contraseña de aplicacion de Google**, sin espacios.
No se usa una API key ni la contraseña habitual de la cuenta.
Para generar esta credencial hay que activar la verificacion en dos pasos y
crear una contraseña de aplicacion en
[la cuenta de Google](https://myaccount.google.com/apppasswords).
Consultar tambien la [ayuda de Gmail](https://support.google.com/mail/answer/7104828?hl=es).
Si la cuenta no ofrece esta opcion, revisar las restricciones de su administrador.

El ejemplo deja configurado `smtp.gmail.com`, puerto `587`, STARTTLS con
certificados verificados y timeout de `10` segundos. `SMTP_FROM_NAME` permite
cambiar el nombre visible; el remitente siempre es `SMTP_USER`.
La aplicacion busca el `.env` dentro de `app`, independientemente del directorio
de ejecucion. Las variables del sistema tienen prioridad. Reiniciar la aplicacion
despues de cambiar las credenciales. El `.env` esta ignorado por Git; no subirlo.

El formulario solicita un email valido y envia el resumen solo despues de
confirmar una compra: fecha, cantidad, pase, total y recordatorio de pago en
boleteria. Si falta configuracion o falla Gmail, la compra sigue confirmada y la
pantalla pide conservar el resumen. No hay reintentos automaticos; no es necesario
repetir la compra. Que el servidor acepte el correo no garantiza su llegada a la
bandeja de entrada: revisar tambien spam.

Las pruebas usan SMTP simulado y no envian correos reales. Para verificar el envio
real, completar las credenciales, iniciar la aplicacion y realizar una compra en
efectivo con una fecha habilitada y un email propio como destinatario.

## Ejecutar las pruebas

Con el entorno virtual activado:

```powershell
python -m pytest -v
```

Tambien se pueden ejecutar solamente las pruebas de la user story:

```powershell
python -m pytest tests/unitarias/test_compra.py -v
```

La opcion `-v` significa `verbose` y muestra el nombre de cada prueba
ejecutada, junto con su resultado.

## Levantar la aplicacion web

Ejecutar:

```powershell
python -m uvicorn app.main:app --reload
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8000
```

La documentacion automatica de FastAPI estara disponible en:

```text
http://127.0.0.1:8000/docs
```

Actualmente estan conectados el formulario, las reglas de compra y la confirmacion
por correo SMTP. El visitante sigue siendo de demostracion; la persistencia y el
pago con tarjeta quedan pendientes.
