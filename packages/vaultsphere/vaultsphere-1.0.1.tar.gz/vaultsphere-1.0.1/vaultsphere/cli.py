import argparse
import json
import sys
import os
from vaultsphere.core import VaultSphere
from vaultsphere.crypto import generate_key
import base64

def main():
    parser = argparse.ArgumentParser(description="CLI para VaultSphere - La NoSQL cifrada 💾🔒")
    parser.add_argument("--dbfile", help="Archivo de base de datos (.vsdb)")
    parser.add_argument("--key", help="Clave de cifrado en base64. Si no se pasa, se genera una nueva", default=None)
    parser.add_argument("--table", help="Nombre de la tabla para la operación", required=False)
    parser.add_argument(
        "--action",
        choices=[
            "create", "delete_db", "list_tables", "insert", "find", "update",
            "delete", "stats", "reset", "backup", "restore", "export", "import"
        ],
        help="Acción a ejecutar",
        required=True,
    )
    parser.add_argument("--data", help="Datos JSON para insert/update", default=None)
    parser.add_argument("--id", help="ID para find/update/delete", default=None)
    parser.add_argument("--backupfile", help="Archivo para backup, restore, export o import", default=None)

    args = parser.parse_args()

    # Manejo de clave
    if args.key:
        try:
            key = base64.b64decode(args.key)
        except Exception:
            print("Clave inválida. Debe ser base64 válida.")
            sys.exit(1)
    else:
        key = generate_key()
        print(f"🔑 Clave generada (guárdala para usar la base): {base64.b64encode(key).decode()}")

    # Tablas config básicas
    tables = {
        "usuarios": {
            "schema": {
                "id": {"type": int, "required": True},
                "nombre": {"type": str, "required": True},
                "edad": {"type": int, "required": False},
            },
            "primaryKey": "id",
            "unique": ["nombre"],
        }
    }

    # Para acciones que necesitan DBfile, valida
    if args.action not in ["create", "delete_db"] and not args.dbfile:
        print("❌ Necesitas especificar --dbfile para esta acción")
        sys.exit(1)

    db = None
    if args.action not in ["create", "delete_db"]:
        db = VaultSphere(args.dbfile, key, tables=tables, autosave=True)

    try:
        if args.action == "create":
            if not args.dbfile:
                print("Necesitas --dbfile para crear una base nueva")
                sys.exit(1)
            # Crear DB vacía y guardar
            db = VaultSphere(args.dbfile, key, tables=tables, autosave=True)
            db.save()
            print(f"🎉 Base de datos creada: {args.dbfile}")

        elif args.action == "delete_db":
            if not args.dbfile:
                print("Necesitas --dbfile para eliminar la base")
                sys.exit(1)
            confirm = input(f"⚠️ Esto borrará '{args.dbfile}'. Escribe 'DELETE' para confirmar: ")
            if confirm == "DELETE":
                try:
                    os.remove(args.dbfile)
                    print("🗑️ Base de datos eliminada.")
                except FileNotFoundError:
                    print("Archivo no encontrado.")
            else:
                print("🚫 Cancelado.")

        elif args.action == "list_tables":
            print("📋 Tablas disponibles:")
            for table in db.tables:
                print(f" - {table}")

        elif args.action == "insert":
            if not args.table or not args.data:
                print("Para insertar necesitas --table y --data")
                sys.exit(1)
            data = json.loads(args.data)
            inserted = db.insert(args.table, data)
            print("✅ Insertado:", inserted)

        elif args.action == "find":
            if not args.table:
                print("Para buscar necesitas --table")
                sys.exit(1)
            if args.id:
                try:
                    _id = int(args.id)
                except:
                    _id = args.id
                doc = db.findById(args.table, _id)
                print(json.dumps(doc, indent=2) if doc else "🔍 No encontrado")
            else:
                results = db.find(args.table)
                print(json.dumps(results, indent=2))

        elif args.action == "update":
            if not args.table or not args.id or not args.data:
                print("Para actualizar necesitas --table, --id y --data")
                sys.exit(1)
            try:
                _id = int(args.id)
            except:
                _id = args.id
            data = json.loads(args.data)
            updated = db.update(args.table, _id, data)
            print("✏️ Actualizado:", updated if updated else "No encontrado")

        elif args.action == "delete":
            if not args.table or not args.id:
                print("Para borrar necesitas --table y --id")
                sys.exit(1)
            try:
                _id = int(args.id)
            except:
                _id = args.id
            deleted = db.delete(args.table, _id)
            print("🗑️ Eliminado" if deleted else "No encontrado")

        elif args.action == "stats":
            stats = db.stats()
            print(json.dumps(stats, indent=2))

        elif args.action == "reset":
            confirm = input("⚠️ Esto eliminará TODOS los datos. Escribe 'YES' para confirmar: ")
            if confirm == "YES":
                db.reset()
                print("♻️ Base de datos reseteada y backup creado.")
            else:
                print("🚫 Cancelado.")

        elif args.action == "backup":
            backup_file = db.backup()
            print(f"💾 Backup creado en: {backup_file}")

        elif args.action == "restore":
            if not args.backupfile:
                print("Para restaurar necesitas --backupfile")
                sys.exit(1)
            db.restore(args.backupfile)
            print("🔄 Restauración completada.")

        elif args.action == "export":
            if not args.table:
                print("Necesitas --table para exportar")
                sys.exit(1)
            data = db.find(args.table)
            outfile = args.backupfile or f"{args.table}_export.json"
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📤 Exportado a {outfile}")

        elif args.action == "import":
            if not args.table or not args.backupfile:
                print("Necesitas --table y --backupfile (archivo JSON) para importar")
                sys.exit(1)
            with open(args.backupfile, "r", encoding="utf-8") as f:
                entries = json.load(f)
            imported_count = 0
            for entry in entries:
                try:
                    db.insert(args.table, entry)
                    imported_count += 1
                except Exception as e:
                    print(f"❌ Error al insertar registro: {e}")
            print(f"📥 {imported_count} registros importados a la tabla '{args.table}'")

        else:
            print("⚠️ Acción no reconocida.")

    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
