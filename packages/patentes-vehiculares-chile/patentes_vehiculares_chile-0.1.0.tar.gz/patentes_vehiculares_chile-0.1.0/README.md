# Patentes Vehiculares Chile

Una librería Python para validar y trabajar con patentes vehiculares chilenas.

## Instalación

```bash
pip install patentes-vehiculares-chile
```

## Uso

```python
from patentes_vehiculares_chile import validar_patente, detectar_tipo_patente, limpiar_patente

# Validar una patente
es_valida = validar_patente("ABCD12")
print(es_valida)  # True o False

# Detectar tipo de patente
tipo = detectar_tipo_patente("AB1234")
print(tipo)  # TipoPatente.ANTIGUA

# Limpiar una patente
patente_limpia = limpiar_patente("  ab-12.34  ")
print(patente_limpia)  # "AB1234"
```

## Características

- Validación de patentes vehiculares chilenas
- Soporte para formatos antiguos y nuevos
- Detección automática del tipo de patente
- Limpieza y normalización de patentes
- Soporte para vehículos, motocicletas y remolques

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.