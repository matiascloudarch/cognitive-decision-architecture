#!/bin/bash

# 1. Limpieza total de puertos
echo "🧹 Liberando puertos 8000 y 8001..."
lsof -ti:8000,8001 | xargs kill -9 2>/dev/null

# 2. Configuración de entorno
export CDA_SECRET_KEY="internal_development_secret_key_fixed_32_chars"
export PYTHONPATH=$(pwd)
source .venv/bin/activate

echo "----------------------------------------"
echo "🚀 Iniciando Servicios CDA"
echo "----------------------------------------"

# 3. Lanzar Kernel
python3 -m uvicorn cda.kernel.engine:app --port 8000 --host 127.0.0.1 > kernel.log 2>&1 &
KERNEL_PID=$!

# 4. Lanzar Gate
python3 -m uvicorn cda.gate.engine:app --port 8001 --host 127.0.0.1 > gate.log 2>&1 &
GATE_PID=$!

echo "⏳ Esperando 5 segundos a que los servicios respondan..."
sleep 5

# 5. Verificación de vida (Crucial)
if ! ps -p $KERNEL_PID > /dev/null; then
    echo "❌ EL KERNEL SE CAYÓ. Error detectado:"
    cat kernel.log
    exit 1
fi

if ! ps -p $GATE_PID > /dev/null; then
    echo "❌ EL GATE SE CAYÓ. Error detectado:"
    cat gate.log
    exit 1
fi

# 6. Ejecutar Test de Integración
echo "🧪 Ejecutando Test de Integración..."
python3 cda/tests/test_integration.py

# 7. Limpieza final
echo "----------------------------------------"
echo "🧹 Apagando servicios..."
kill -9 $KERNEL_PID $GATE_PID 2>/dev/null
echo "✨ Proceso finalizado."
