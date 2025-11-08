# Acceso Super Admin - Sistema Electoral Caquetá

## ✅ Configuración Completada

El sistema está funcionando correctamente con acceso completo para el Super Administrador.

## 🔐 Credenciales de Acceso

```
Username: superadmin
Password: admin123
```

## 🌐 URLs de Acceso

### Servidor Local
- **Aplicación**: http://127.0.0.1:5000
- **Login**: http://127.0.0.1:5000/login
- **Dashboard Super Admin**: http://127.0.0.1:5000/dashboard/super_admin

### Red Local
- **Aplicación**: http://192.168.20.61:5000
- **Login**: http://192.168.20.61:5000/login
- **Dashboard Super Admin**: http://192.168.20.61:5000/dashboard/super_admin

## 👤 Información del Usuario

- **ID**: 1
- **Username**: superadmin
- **Nombre Completo**: Super Administrador
- **Email**: superadmin@caqueta.gov.co
- **Rol**: super_admin
- **Estado**: Activo ✅

## 🎯 Funcionalidades del Super Admin

### 1. Gestión de Usuarios
- Crear, editar y eliminar usuarios
- Asignar roles y permisos
- Gestionar accesos por municipio/puesto

### 2. Configuración del Sistema
- Configurar procesos electorales
- Definir cargos electorales
- Gestionar partidos políticos y coaliciones

### 3. Gestión de Candidatos
- Registrar candidatos
- Asignar a partidos y coaliciones
- Configurar prioridades

### 4. Coordinación Electoral
- Supervisar coordinadores departamentales
- Supervisar coordinadores municipales
- Supervisar coordinadores de puesto

### 5. Gestión de Testigos
- Asignar testigos a mesas
- Revisar capturas E14
- Validar observaciones e incidencias

### 6. Reportes y Consolidación
- Generar reportes E24
- Consolidar resultados
- Exportar datos

### 7. Prioridades
- Configurar prioridades de municipios
- Configurar prioridades de partidos
- Configurar prioridades de candidatos
- Configurar prioridades de procesos

### 8. Auditoría
- Ver logs del sistema
- Revisar actividad de usuarios
- Monitorear incidencias

## 📊 Estado del Sistema

### Base de Datos
- **Archivo**: caqueta_electoral.db
- **Tablas**: 44 tablas
- **Usuarios**: 6 usuarios registrados
- **Candidatos**: 5 candidatos
- **Mesas**: 15 mesas de votación
- **Municipios**: 6 municipios

### Usuarios Registrados

| Username | Rol | Nombre |
|----------|-----|--------|
| superadmin | super_admin | Super Administrador |
| coord_dept | coordinador_departamental | Carlos Mendoza |
| coord_mun | coordinador_municipal | Ana Patricia Ruiz |
| coord_puesto | coordinador_puesto | Miguel Torres |
| testigo_electoral | testigo_electoral | Laura González |
| testigo_mesa | testigo_mesa | Juan Pérez |

## 🔧 Comandos Útiles

### Iniciar el Servidor
```powershell
python app.py
```

### Resetear Contraseña del Super Admin
```powershell
python reset_superadmin.py
```

### Verificar Usuarios
```powershell
python check_users.py
```

### Verificar Tablas de la Base de Datos
```powershell
python check_db_tables.py
```

### Probar Login
```powershell
python test_superadmin_login.py
```

## 🚀 Proceso de Login

### 1. Acceso Web
1. Abrir navegador
2. Ir a http://127.0.0.1:5000/login
3. Ingresar credenciales:
   - Username: `superadmin`
   - Password: `admin123`
4. Click en "Iniciar Sesión"
5. Serás redirigido al dashboard

### 2. Acceso API
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"cedula":"superadmin","password":"admin123"}'
```

Respuesta exitosa:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "superadmin",
    "nombre_completo": "Super Administrador",
    "rol": "super_admin"
  }
}
```

## 📱 Dashboards Disponibles

### Por Rol
- `/dashboard/super_admin` - Super Administrador
- `/dashboard/admin_departamental` - Admin Departamental
- `/dashboard/admin_municipal` - Admin Municipal
- `/dashboard/coordinador_electoral` - Coordinador Electoral
- `/dashboard/coordinador_departamental` - Coordinador Departamental
- `/dashboard/coordinador_municipal` - Coordinador Municipal
- `/dashboard/coordinador_puesto` - Coordinador de Puesto
- `/dashboard/testigo_mesa` - Testigo de Mesa
- `/dashboard/auditor_electoral` - Auditor Electoral
- `/dashboard/observador_internacional` - Observador Internacional

## 🔒 Seguridad

### Autenticación
- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Tokens JWT para sesiones
- ✅ Validación de usuarios activos
- ✅ Verificación de roles

### Recomendaciones
1. Cambiar la contraseña por defecto en producción
2. Usar HTTPS en producción
3. Configurar variables de entorno para secrets
4. Implementar rate limiting
5. Habilitar logs de auditoría

## 📚 Documentación Adicional

- **README.md** - Documentación general del proyecto
- **REQUERIMIENTOS_SISTEMA_COMPLETO.md** - Requerimientos consolidados
- **.kiro/specs/** - Especificaciones detalladas
- **LIMPIEZA_PROYECTO.md** - Información sobre la limpieza del proyecto

## ⚙️ Configuración del Servidor

### Modo Desarrollo (Actual)
- Debug: ON
- Host: 0.0.0.0
- Port: 5000
- Reloader: ON

### Para Producción
```powershell
# Usar WSGI
python wsgi.py

# O con gunicorn (si está instalado)
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 🎉 Estado Actual

✅ Servidor corriendo  
✅ Base de datos configurada  
✅ Super Admin con acceso completo  
✅ Login funcionando correctamente  
✅ Dashboard accesible  
✅ APIs funcionando  
✅ Módulos cargados  

## 📞 Soporte

Si necesitas ayuda adicional:
1. Revisa los logs del servidor
2. Verifica la base de datos con los scripts de verificación
3. Consulta la documentación en `/docs/`

---

**Última actualización**: 7 de noviembre de 2025  
**Versión del sistema**: 1.0.0  
**Estado**: ✅ Operativo
