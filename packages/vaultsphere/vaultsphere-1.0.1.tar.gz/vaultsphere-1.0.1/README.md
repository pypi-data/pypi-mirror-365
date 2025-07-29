# 🔐 VaultSphere

> **La base de datos NoSQL cifrada más brutal y sencilla para Python.**  
> Guarda tus datos en JSON, pero con toda la seguridad y flexibilidad que necesitas.  

---

## ✨ Características que te van a encantar

- 🔒 **Cifrado súper seguro** con Fernet (AES 128-bit).  
- 📋 **Esquemas validados** para que tus datos sean siempre impecables.  
- 🔍 **Consultas estilo MongoDB** con operadores poderosos (`$gt`, `$in`, `$ne` y más).  
- 🚀 **Índices únicos** para acelerar búsquedas y evitar duplicados.  
- 💾 **Backups automáticos** y restauración sin drama.  
- 🔄 **Transacciones con rollback** para operaciones seguras.  
- 🖥️ **CLI interactivo** para controlar todo desde la terminal.  
- 🔔 **Hooks en carga y guardado** para que le metas magia personalizada.  

---

## 🚀 Instalación

Solo corre:

```bash
pip install vaultsphere
````

---

## 🛠️ Cómo usarlo (Ejemplo rápido)

```python
from vaultsphere import VaultSphere, generate_key

# 🔑 Genera tu clave secreta y guárdala bien
key = generate_key()

# 📂 Define tus tablas y sus reglas (schema)
tables = {
    "usuarios": {
        "schema": {
            "id": {"type": int, "required": True},
            "nombre": {"type": str, "required": True},
            "edad": {"type": int, "required": False}
        },
        "primaryKey": "id",
        "unique": ["nombre"]
    }
}

# 🗄️ Crea o abre la base de datos cifrada
db = VaultSphere("mi_db.vsdb", key, tables)

# ➕ Inserta un usuario nuevo
usuario = db.insert("usuarios", {"id": 1,"nombre": "Pedro", "edad": 18})

# 🔎 Busca todos los usuarios mayores o iguales a 18 años
usuarios_mayores = db.find("usuarios", {"edad": {"$gte": 18}})

# ✍️ Actualiza datos del usuario
db.update("usuarios", usuario["id"], {"edad": 19})

# ❌ Borra al usuario
db.delete("usuarios", usuario["id"])

# 💾 Guarda los cambios si usas autosave=False
db.save()

# 📦 Haz un backup manual
ruta_backup = db.backup()

# ♻️ Restaura un backup cuando quieras
db.restore(ruta_backup)
```

---

## 💻 CLI: Controla tu VaultSphere desde la consola

Ejecuta:

```bash
vaultsphere
```

Y usa estos comandos:

| Comando                      | Qué hace                         |
| ---------------------------- | -------------------------------- |
| `insert <tabla> <json>`      | Inserta un nuevo documento       |
| `read <tabla> <id>`          | Lee un documento por su ID       |
| `update <tabla> <id> <json>` | Actualiza un documento existente |
| `remove <tabla> <id>`        | Elimina un documento por ID      |
| `exit`                       | Salir del CLI                    |

Ejemplo:

```
VaultSphere> insert usuarios {"nombre": "Juan", "edad": 20}
VaultSphere> read usuarios 1
VaultSphere> update usuarios 1 {"edad": 21}
VaultSphere> remove usuarios 1
VaultSphere> exit
```

---

## 📄 Licencia

MIT License © 2025 zzzNeet

---

## ✨ Versiones

🎓 JS: [VaultSphereJS](https://www.npmjs.com/package/vaultspherejs)
🧪 Experimental: [VaultSphere](https://test.pypi.org/project/vaultsphere/)

---

## 📬 Contacto

¿Tienes dudas, ideas o solo quieres saludar?

💌 Discord: `.simplyneet`
🐙 GitHub: [github.com/simplyneet](https://github.com/simplyneet/vaultsphere)