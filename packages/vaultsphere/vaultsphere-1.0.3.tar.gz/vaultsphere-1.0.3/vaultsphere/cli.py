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
    parser.add_argument("--action", choices=[
        "create", "delete_db", "create_table", "drop_table", "clone_table", "rename_table",
        "insert", "find", "findone", "update", "delete",
        "stats", "reset", "backup", "restore",
        "list_tables", "export", "import",
        "rebuild_indexes", "compact", "info"
    ], help="Acción a ejecutar", required=True)
    parser.add_argument("--data", help="Datos JSON para insert/update o nuevo nombre para rename_table", default=None)
    parser.add_argument("--id", help="ID para find/update/delete", default=None)
    parser.add_argument("--backupfile", help="Archivo de backup para restore/export/import", default=None)
    parser.add_argument("--schema", help="Esquema de la tabla en formato JSON (e.g. '{\"nombre\": \"str\", \"edad\": \"int\"}')", default=None)


    args = parser.parse_args()

    
    if args.key:
        try:
            key = base64.b64decode(args.key)
        except Exception:
            print("Clave inválida. Debe ser base64 válida.")
            sys.exit(1)
    else:
        key = generate_key()
        print(f"🔑 Clave generada (guárdala para usar la base): {base64.b64encode(key).decode()}")

    
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

    
    if args.action == "create":
        if not args.dbfile:
            print("Necesitas --dbfile para crear una base nueva")
            sys.exit(1)
        db = VaultSphere(args.dbfile, key, tables=tables, autosave=True)
        db.save()
        print(f"Base de datos creada: {args.dbfile}")
        sys.exit(0)

    
    if not args.dbfile:
        print("Necesitas --dbfile para esta acción")
        sys.exit(1)

    if not os.path.exists(args.dbfile):
        print(f"Archivo {args.dbfile} no existe. Usa 'create' para crear uno nuevo.")
        sys.exit(1)

    db = VaultSphere(args.dbfile, key, tables=tables, autosave=True)

    try:
        if args.action == "delete_db":
            confirm = input(f"⚠️ Esto borrará '{args.dbfile}'. Escribe 'DELETE' para confirmar: ")
            if confirm == "DELETE":
                os.remove(args.dbfile)
                print("Base de datos eliminada.")
            else:
                print("Cancelado.")

        elif args.action == "create_table":
            if not args.table:
                print("Necesitas --table para crear tabla")
                sys.exit(1)
            if args.table in db.tables:
                print("La tabla ya existe.")
                sys.exit(1)
            
            if not args.schema:
                print("❌ Necesitas pasar --schema para crear una tabla")
                sys.exit(1)

            try:
                schema_input = json.loads(args.schema)

            except json.JSONDecodeError:
                print("❌ Esquema inválido. Debe ser JSON válido.")
                sys.exit(1)
            type_map = {
                "str": str,
                "int": int,
                "float": float,
                "bool": bool
            }

            schema = {}
            for field, field_type in schema_input.items():
                if field_type not in type_map:
                    print(f"❌ Tipo '{field_type}' no soportado. Usa 'str', 'int', 'float' o 'bool'.")
                    sys.exit(1)
                schema[field] = {"type": type_map[field_type], "required": True}

            if "id" not in schema:
                schema["id"] = {"type": int, "required": True}

            db.tables[args.table] = {
                "schema": schema,
                "primaryKey": "id",
                "unique": []
            }
            db.data[args.table] = []
            db.save()
            print(f"✅ Tabla '{args.table}' creada con esquema: {list(schema.keys())}")

        elif args.action == "drop_table":
            if not args.table:
                print("Necesitas --table para eliminar tabla")
                sys.exit(1)
            if args.table not in db.tables:
                print("La tabla no existe.")
                sys.exit(1)
            db.drop_table(args.table)
            print(f"Tabla '{args.table}' eliminada.")

        elif args.action == "clone_table":
            if not args.table or not args.data:
                print("Necesitas --table (origen) y --data (nuevo nombre) para clonar tabla")
                sys.exit(1)
            if args.data in db.tables:
                print("La tabla destino ya existe.")
                sys.exit(1)
            db.clone_table(args.table, args.data)
            print(f"Tabla '{args.table}' clonada como '{args.data}'.")

        elif args.action == "rename_table":
            if not args.table or not args.data:
                print("Necesitas --table (actual) y --data (nuevo nombre) para renombrar tabla")
                sys.exit(1)
            if args.data in db.tables:
                print("La tabla destino ya existe.")
                sys.exit(1)
            db.rename_table(args.table, args.data)
            print(f"Tabla '{args.table}' renombrada como '{args.data}'.")

        elif args.action == "insert":
            if not args.table or not args.data:
                print("Para insertar necesitas --table y --data")
                sys.exit(1)
            data = json.loads(args.data)
            inserted = db.insert(args.table, data)
            print("Insertado:", inserted)

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
                if doc:
                    print(json.dumps(doc, indent=2, ensure_ascii=False))
                else:
                    print("No encontrado")
            else:
                results = db.find(args.table)
                print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.action == "findone":
            if not args.table or not args.data:
                print("Para findone necesitas --table y --data (query JSON)")
                sys.exit(1)
            query = json.loads(args.data)
            doc = db.findOne(args.table, query)
            if doc:
                print(json.dumps(doc, indent=2, ensure_ascii=False))
            else:
                print("No encontrado")

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
            if updated:
                print("Actualizado:", updated)
            else:
                print("No encontrado")

        elif args.action == "delete":
            if not args.table or not args.id:
                print("Para borrar necesitas --table y --id")
                sys.exit(1)
            try:
                _id = int(args.id)
            except:
                _id = args.id
            deleted = db.delete(args.table, _id)
            print("Eliminado" if deleted else "No encontrado")

        elif args.action == "stats":
            stats = db.stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))

        elif args.action == "info":
            info = db.info()
            print(info)

        elif args.action == "reset":
            confirm = input("⚠️ Esto eliminará TODOS los datos. Escribe 'YES' para confirmar: ")
            if confirm == "YES":
                db.reset()
                print("Base de datos reseteada y backup creado.")
            else:
                print("Cancelado.")

        elif args.action == "backup":
            backup_file = db.backup()
            print(f"Backup creado en: {backup_file}")

        elif args.action == "restore":
            if not args.backupfile:
                print("Para restaurar necesitas --backupfile")
                sys.exit(1)
            db.restore(args.backupfile)
            print("Restauración completada.")

        elif args.action == "list_tables":
            print("Tablas disponibles:")
            for table in db.tables:
                print(f" - {table}")

        elif args.action == "export":
            if not args.table:
                print("Necesitas --table para exportar")
                sys.exit(1)
            data = db.find(args.table)
            outfile = args.backupfile or f"{args.table}_export.json"
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Exportado a {outfile}")

        elif args.action == "import":
            if not args.table or not args.backupfile:
                print("Necesitas --table y --backupfile (archivo JSON) para importar")
                sys.exit(1)
            with open(args.backupfile, "r", encoding="utf-8") as f:
                entries = json.load(f)
            inserted_count = 0
            for entry in entries:
                try:
                    db.insert(args.table, entry)
                    inserted_count += 1
                except Exception as e:
                    print(f"Error al insertar registro: {e}")
            print(f"{inserted_count} registros importados a la tabla '{args.table}'")

        elif args.action == "rebuild_indexes":
            db.rebuild_indexes()
            print("Índices reconstruidos.")

        elif args.action == "compact":
            db.compact()
            print("Base compactada y guardada.")

        else:
            print("Acción no reconocida.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
