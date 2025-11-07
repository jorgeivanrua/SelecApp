
# Agregar esta función al archivo app.py para soportar login con cédula

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de autenticación con cédula"""
    try:
        data = request.get_json()
        cedula = data.get('cedula') or data.get('username')  # Soportar ambos
        password = data.get('password')
        
        if not cedula or not password:
            return jsonify({'error': 'Cédula and password required'}), 400
        
        # Buscar usuario por cédula o username
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, nombre_completo, password_hash, rol, activo
            FROM users 
            WHERE (cedula = ? OR username = ?) AND activo = 1
        """, (cedula, cedula))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verificar password
        if not check_password_hash(user_data[3], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Crear token JWT
        access_token = create_access_token(
            identity=user_data[0],
            additional_claims={
                'username': user_data[1],
                'role': user_data[4]
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user_data[0],
                'username': user_data[1],
                'nombre_completo': user_data[2],
                'rol': user_data[4]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
