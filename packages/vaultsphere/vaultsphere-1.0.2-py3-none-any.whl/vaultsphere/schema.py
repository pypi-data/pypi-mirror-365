def validate_document(doc: dict, schema: dict, path: str = '') -> None:
    for field, rules in schema.items():
        field_path = f"{path}.{field}" if path else field

        # Requerido
        if rules.get('required') and field not in doc:
            raise ValueError(f"Campo obligatorio '{field_path}' no encontrado.")

        if field in doc:
            val = doc[field]

            # Nulo permitido
            if val is None:
                if not rules.get('nullable', False):
                    raise ValueError(f"Campo '{field_path}' no puede ser None.")
                continue

            # Tipos múltiples o únicos
            expected_type = rules.get('type')
            if expected_type:
                if not isinstance(expected_type, (list, tuple)):
                    expected_type = [expected_type]
                if not any(isinstance(val, t) for t in expected_type):
                    tipos = ", ".join(t.__name__ for t in expected_type)
                    raise TypeError(f"Campo '{field_path}' debe ser de tipo(s) {tipos}, no {type(val).__name__}.")

            # Valores permitidos
            if 'allowed' in rules and val not in rules['allowed']:
                raise ValueError(f"Campo '{field_path}' debe ser uno de {rules['allowed']}, no '{val}'.")

            # Rango de números
            if isinstance(val, (int, float)):
                if 'min' in rules and val < rules['min']:
                    raise ValueError(f"Campo '{field_path}' debe ser ≥ {rules['min']}.")
                if 'max' in rules and val > rules['max']:
                    raise ValueError(f"Campo '{field_path}' debe ser ≤ {rules['max']}.")

            # Longitud (strings, listas, etc.)
            if isinstance(val, (str, list, tuple, dict)):
                if 'min_length' in rules and len(val) < rules['min_length']:
                    raise ValueError(f"Campo '{field_path}' debe tener longitud ≥ {rules['min_length']}.")
                if 'max_length' in rules and len(val) > rules['max_length']:
                    raise ValueError(f"Campo '{field_path}' debe tener longitud ≤ {rules['max_length']}.")

            # Sub-documento
            if isinstance(val, dict) and 'schema' in rules:
                validate_document(val, rules['schema'], path=field_path)

            # Función de validación personalizada
            if 'validator' in rules:
                validator_fn = rules['validator']
                if not validator_fn(val):
                    raise ValueError(f"Campo '{field_path}' no pasó la validación personalizada.")
