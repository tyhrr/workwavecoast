#!/bin/bash

# Quick deployment verification script
# Run this locally to test if your deployment config is working

echo "🔍 Verificando configuración de deployment..."

echo ""
echo "📋 Archivos de configuración:"
echo "✓ Procfile:" && cat Procfile 2>/dev/null || echo "❌ Procfile no encontrado"
echo "✓ render.yaml:" && head -10 render.yaml 2>/dev/null || echo "❌ render.yaml no encontrado"
echo "✓ requirements.txt:" && head -3 requirements.txt 2>/dev/null || echo "❌ requirements.txt no encontrado"

echo ""
echo "🔧 Scripts de deployment:"
echo "✓ build.sh:" && cat build.sh 2>/dev/null || echo "❌ build.sh no encontrado"
echo "✓ start.sh:" && cat start.sh 2>/dev/null || echo "❌ start.sh no encontrado"

echo ""
echo "⚙️ Configuración de Gunicorn:"
echo "✓ gunicorn_config.py:" && ls backend/gunicorn_config.py 2>/dev/null || echo "❌ gunicorn_config.py no encontrado"

echo ""
echo "🚀 URLs para probar después del deployment:"
echo "• Health Check: https://workwavecoast.onrender.com/api/health"
echo "• Status Check: https://workwavecoast.onrender.com/api/system-status"
echo "• Frontend: https://workwavecoast.onrender.com/"
echo "• Admin Panel: https://workwavecoast.onrender.com/admin"
