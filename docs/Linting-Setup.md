# Guía de Configuración de Linting y Formateo

Este documento explica cómo está configurado el linting y formateo en el proyecto, y cómo asegurar que los agentes de IA sigan estas reglas.

## 🛠️ Herramientas Configuradas

### 1. Ruff - Linter y Formateador Principal
Configurado en `backend/pyproject.toml`:
- **Longitud máxima de línea**: 100 caracteres
- **Reglas activas**: E, F, I, N, W, UP
- **Target**: Python 3.11

### 2. VS Code - Integración con el Editor
Configurado en `.vscode/settings.json`:
- ✅ Formateo automático al guardar
- ✅ Organización automática de imports
- ✅ Fix automático de problemas de linting
- ✅ Muestra errores en tiempo real
- ✅ Línea guía en la columna 100

### 3. Pre-commit Hooks
Configurado en `.pre-commit-config.yaml`:
- ✅ Ejecuta ruff automáticamente antes de cada commit
- ✅ Verifica YAML, JSON, TOML
- ✅ Elimina espacios en blanco finales
- ✅ Asegura salto de línea final

### 4. GitHub Copilot Instructions
Configurado en `.github/copilot-instructions.md`:
- ✅ Define estándares de código para IA
- ✅ Ejemplos de patrones a seguir
- ✅ Reglas de formateo específicas

## 🚀 Instalación y Configuración

### Paso 1: Instalar la extensión de Ruff en VS Code
La extensión ya está instalada: `charliermarsh.ruff`

Si necesitas reinstalarla:
```bash
code --install-extension charliermarsh.ruff
```

### Paso 2: Instalar Pre-commit Hooks
```bash
make pre-commit-install
```

O manualmente:
```bash
cd backend && poetry run pre-commit install
```

### Paso 3: Verificar que todo funciona
```bash
make lint
```

## 📝 Comandos Disponibles

### Verificar código (solo lectura)
```bash
make lint
```

### Corregir automáticamente
```bash
make lint-fix
```

### Solo formatear
```bash
make format
```

### Ejecutar pre-commit manualmente
```bash
cd backend && poetry run pre-commit run --all-files
```

## 🤖 Cómo los Agentes de IA Siguen las Reglas

### GitHub Copilot
1. **Lee automáticamente** `.github/copilot-instructions.md`
2. Genera código siguiendo los estándares definidos
3. Respeta la longitud de línea de 100 caracteres
4. Ordena imports correctamente

### Claude/AI Agents
1. **Leen las instrucciones** en el archivo copilot-instructions.md
2. Antes de considerar código completo, verifican con ruff
3. Siguen los patrones de importación definidos
4. Incluyen type hints y docstrings

## 🔄 Flujo de Trabajo Recomendado

### Al escribir código:
1. **Escribe código** - VS Code mostrará errores en tiempo real
2. **Guarda archivo** - Formateo automático se aplica
3. **Commit** - Pre-commit hooks verifican todo nuevamente

### Si hay errores de linting:
```bash
# Ver qué está mal
make lint

# Corregir automáticamente
make lint-fix

# Si algo no se corrigió automáticamente, VS Code te mostrará el error
```

## 📋 Reglas Principales

### Imports
```python
# ✅ CORRECTO - Ordenado: stdlib, third-party, local
import os
from datetime import datetime

import httpx
from fastapi import APIRouter

from src.domain.entities import User
```

### Longitud de Línea
```python
# ❌ INCORRECTO - Más de 100 caracteres
result = some_very_long_function_name(parameter1, parameter2, parameter3, parameter4, parameter5)

# ✅ CORRECTO - Dividido en múltiples líneas
result = some_very_long_function_name(
    parameter1, parameter2, parameter3, parameter4, parameter5
)
```

### Type Hints
```python
# ✅ CORRECTO
def process_data(input_data: str, limit: int = 10) -> dict[str, Any]:
    """Process input data and return results."""
    pass
```

### Docstrings
```python
# ✅ CORRECTO
def my_function(param: str) -> bool:
    """Short description.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    pass
```

## 🔍 Verificación en CI/CD

El linting también se ejecuta en GitHub Actions (si está configurado):
- Verifica código en cada PR
- Previene merge si hay errores de linting
- Asegura calidad de código consistente

## 💡 Tips

1. **Usa `make lint-fix`** antes de hacer commit para corregir la mayoría de problemas automáticamente
2. **Confía en VS Code** - Te mostrará errores en tiempo real con subrayados rojos
3. **Pre-commit hooks** evitarán que hagas commit con errores de linting
4. **Los agentes de IA** seguirán las reglas si mencionas "siguiendo las reglas de linting del proyecto"

## 🐛 Solución de Problemas

### Ruff no se ejecuta en VS Code
1. Verifica que la extensión está instalada: `charliermarsh.ruff`
2. Recarga VS Code: `Cmd+Shift+P` → "Reload Window"
3. Verifica la ruta del intérprete de Python

### Pre-commit hooks no funcionan
```bash
# Reinstalar hooks
cd backend
poetry run pre-commit uninstall
poetry run pre-commit install

# Probar manualmente
poetry run pre-commit run --all-files
```

### Conflictos con Black u otros formateadores
Este proyecto usa **solo Ruff**. Si tienes Black u otros formateadores, desactívalos en `.vscode/settings.json`.
