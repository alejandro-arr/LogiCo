# LogiCo - Discopro

Proyecto Django conectado a MySQL/MariaDB usando XAMPP.

## Usuarios disponibles

| Tipo | Usuario | Contrasena | Acceso |
| --- | --- | --- | --- |
| Administrador | `admin` | `Admin12345` | Acceso a todas las secciones y al panel `/admin/` |
| Usuario generico | `usuario` | `Usuario12345` | Acceso al sistema web |

## Requisitos

- XAMPP instalado.
- MySQL/MariaDB iniciado desde el panel de XAMPP.
- Python 3.12 instalado.
- Entorno virtual del proyecto en `venv`.

## Base de datos en XAMPP

El proyecto usa esta configuracion en `proyecto_logico/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'logico_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Antes de migrar, abre XAMPP y enciende `MySQL`. Luego entra a phpMyAdmin:

```text
http://localhost/phpmyadmin/
```

Crea una base de datos llamada:

```text
logico_db
```

## Ejecutar migraciones

Desde PowerShell, entra a la carpeta donde esta `manage.py`:

```powershell
cd C:\Users\rafac\OneDrive\Escritorio\discopro\discopro
```

Activa el entorno virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

Si necesitas instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Crea migraciones cuando cambies modelos:

```powershell
python manage.py makemigrations
```

Aplica las migraciones en XAMPP/MySQL:

```powershell
python manage.py migrate
```

Verifica que el proyecto este correcto:

```powershell
python manage.py check
```

## Ejecutar servidor

Con MySQL encendido en XAMPP, ejecuta:

```powershell
python manage.py runserver
```

Abre:

```text
http://127.0.0.1:8000/login/
```

Panel administrador de Django:

```text
http://127.0.0.1:8000/admin/
```

## Analisis con SonarQube

Con SonarQube iniciado en:

```text
http://localhost:9000
```

Define el token solo en la terminal:

```powershell
$env:SONAR_TOKEN='tu_token_de_sonarqube'
```

Ejecuta el analisis:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_sonar.ps1
```

Tambien puedes ejecutar pysonar directo:

```powershell
pysonar --sonar-host-url=http://localhost:9000 --sonar-token $env:SONAR_TOKEN --sonar-project-key=logico
```

## Crear usuarios

Solo el administrador debe registrar usuarios desde el apartado:

```text
http://127.0.0.1:8000/usuarios/
```

El login publico no permite crear usuarios.
