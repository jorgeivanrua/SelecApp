#!/bin/bash
# Script de backup automático para Sistema Electoral ERP

set -e

# Configuración
DB_HOST="db"
DB_PORT="5432"
DB_NAME="caqueta_electoral"
DB_USER="electoral_user"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "🔄 Iniciando backup del Sistema Electoral ERP - $DATE"

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

# Backup de la base de datos
echo "📊 Creando backup de la base de datos..."
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --no-password --verbose --clean --no-owner --no-privileges \
    > $BACKUP_DIR/db_backup_$DATE.sql

# Comprimir el backup
echo "🗜️  Comprimiendo backup..."
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Verificar que el backup se creó correctamente
if [ -f "$BACKUP_DIR/db_backup_$DATE.sql.gz" ]; then
    echo "✅ Backup creado exitosamente: db_backup_$DATE.sql.gz"
    
    # Obtener tamaño del archivo
    SIZE=$(du -h $BACKUP_DIR/db_backup_$DATE.sql.gz | cut -f1)
    echo "📏 Tamaño del backup: $SIZE"
else
    echo "❌ Error: No se pudo crear el backup"
    exit 1
fi

# Limpiar backups antiguos
echo "🧹 Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
find $BACKUP_DIR -name "db_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Contar backups restantes
BACKUP_COUNT=$(find $BACKUP_DIR -name "db_backup_*.sql.gz" -type f | wc -l)
echo "📁 Backups disponibles: $BACKUP_COUNT"

# Log del backup
echo "$(date): Backup completado - db_backup_$DATE.sql.gz ($SIZE)" >> $BACKUP_DIR/backup.log

echo "✅ Proceso de backup completado exitosamente"