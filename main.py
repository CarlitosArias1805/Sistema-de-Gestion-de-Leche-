import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN A MYSQL
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'CarlosArias1805', 
    'database': 'ControlLecheDB'
}

def obtener_conexion():
    """Retorna una conexión activa a MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

# ==========================================
# VENTANA PRINCIPAL DEL SISTEMA (DASHBOARD)
# ==========================================
def abrir_sistema_principal(ventana_login):
    ventana_login.destroy()  # Cierra la ventana de inicio de sesión

    dashboard = tk.Tk()
    dashboard.title("Leche de Campo - Panel de Gestión y Control")
    dashboard.geometry("950x650")
    dashboard.configure(bg="#F3F7F4")

    # --- ENCABEZADO ---
    header = tk.Frame(dashboard, bg="#123B65", height=70)
    header.pack(side="top", fill="x")
    
    tk.Label(
        header, text="SISTEMA DE GESTIÓN DE PRODUCCIÓN Y COMERCIALIZACIÓN",
        font=("Arial", 15, "bold"), fg="white", bg="#123B65"
    ).pack(pady=(10, 2))
    
    tk.Label(
        header, text="Asociación de Productores de Leche - Cotopaxi",
        font=("Arial", 10), fg="#DCEAF5", bg="#123B65"
    ).pack(pady=(0, 10))

    # --- PESTAÑAS DEL SISTEMA ---
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill="both", expand=True, padx=15, pady=15)

    # ------------------------------------------
    # PESTAÑA 1: REGISTRO Y SITUACIÓN CRÍTICA
    # ------------------------------------------
    tab_operaciones = tk.Frame(notebook, bg="white", padx=15, pady=15)
    notebook.add(tab_operaciones, text="📋 Registro y Situación Crítica")

    # Panel Izquierdo: Registro Diario de Entrega
    frame_registro = tk.LabelFrame(tab_operaciones, text=" 1. Registro Diario de Entregas ", font=("Arial", 11, "bold"), bg="white", fg="#123B65", padx=15, pady=15)
    frame_registro.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    tk.Label(frame_registro, text="ID Productor:", bg="white", font=("Arial", 10)).pack(anchor="w", pady=(5,0))
    entry_prod_id = tk.Entry(frame_registro, font=("Arial", 11), relief="solid", bd=1)
    entry_prod_id.pack(fill="x", pady=(0, 10))

    tk.Label(frame_registro, text="Litros Entregados:", bg="white", font=("Arial", 10)).pack(anchor="w", pady=(5,0))
    entry_litros = tk.Entry(frame_registro, font=("Arial", 11), relief="solid", bd=1)
    entry_litros.pack(fill="x", pady=(0, 15))

    def registrar_entrega_bd():
        try:
            prod_id = int(entry_prod_id.get())
            litros = float(entry_litros.get())

            if litros <= 0:
                messagebox.showwarning("Advertencia", "La cantidad de litros debe ser mayor a 0.")
                return

            conn = obtener_conexion()
            cursor = conn.cursor()
            query = "INSERT INTO Entregas (ProductorID, LitrosEntregados) VALUES (%s, %s)"
            cursor.execute(query, (prod_id, litros))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Éxito", f"¡Entrega registrada exitosamente en MySQL para el Productor #{prod_id}!")
            entry_prod_id.delete(0, tk.END)
            entry_litros.delete(0, tk.END)
            actualizar_tabla_entregas()
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
        except Exception as err:
            messagebox.showerror("Error BD", f"No se pudo guardar: {err}")

    tk.Button(frame_registro, text="Guardar Entrega", font=("Arial", 10, "bold"), bg="#168447", fg="white", cursor="hand2", command=registrar_entrega_bd).pack(fill="x", ipady=6)

    # Panel Derecho: Situación Crítica (Corrección Autorizada)
    frame_critico = tk.LabelFrame(tab_operaciones, text=" 2. Corrección Autorizada (Situación Crítica) ", font=("Arial", 11, "bold"), bg="white", fg="#A31313", padx=15, pady=15)
    frame_critico.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    tk.Label(frame_critico, text="ID Entrega a corregir:", bg="white", font=("Arial", 10)).pack(anchor="w")
    entry_entrega_id = tk.Entry(frame_critico, font=("Arial", 11), relief="solid", bd=1)
    entry_entrega_id.pack(fill="x", pady=(0, 5))

    tk.Label(frame_critico, text="Litros Correctos (Nuevos):", bg="white", font=("Arial", 10)).pack(anchor="w")
    entry_litros_nuevos = tk.Entry(frame_critico, font=("Arial", 11), relief="solid", bd=1)
    entry_litros_nuevos.pack(fill="x", pady=(0, 5))

    tk.Label(frame_critico, text="Motivo del cambio:", bg="white", font=("Arial", 10)).pack(anchor="w")
    entry_motivo = tk.Entry(frame_critico, font=("Arial", 11), relief="solid", bd=1)
    entry_motivo.pack(fill="x", pady=(0, 5))

    tk.Label(frame_critico, text="Usuario que autoriza:", bg="white", font=("Arial", 10)).pack(anchor="w")
    entry_usuario_auth = tk.Entry(frame_critico, font=("Arial", 11), relief="solid", bd=1)
    entry_usuario_auth.pack(fill="x", pady=(0, 10))

    def aplicar_correccion_critica():
        try:
            e_id = int(entry_entrega_id.get())
            l_nuevos = float(entry_litros_nuevos.get())
            motivo = entry_motivo.get().strip()
            usr = entry_usuario_auth.get().strip() or "Admin"

            if not motivo:
                messagebox.showwarning("Advertencia", "Debe especificar el motivo del cambio para auditoría.")
                return

            conn = obtener_conexion()
            cursor = conn.cursor()

            # Consultar valor anterior
            cursor.execute("SELECT LitrosEntregados FROM Entregas WHERE EntregaID = %s", (e_id,))
            res = cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "No existe la entrega especificada.")
                conn.close()
                return
            l_anteriores = res[0]

            # 1. Trazabilidad en Tabla Auditoría
            query_audit = """INSERT INTO AuditoriaEntregas 
                            (EntregaID, LitrosAnteriores, LitrosNuevos, MotivoCambio, UsuarioAutoriza) 
                            VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query_audit, (e_id, l_anteriores, l_nuevos, motivo, usr))

            # 2. Actualizar la Entrega
            query_update = "UPDATE Entregas SET LitrosEntregados = %s, Estado = 'Corregida' WHERE EntregaID = %s"
            cursor.execute(query_update, (l_nuevos, e_id))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Situación Crítica Resuelta", f"Corrección guardada y registrada en Auditoría.\nAnterior: {l_anteriores}L -> Nuevo: {l_nuevos}L")
            entry_entrega_id.delete(0, tk.END)
            entry_litros_nuevos.delete(0, tk.END)
            entry_motivo.delete(0, tk.END)
            entry_usuario_auth.delete(0, tk.END)
            actualizar_tabla_entregas()
        except Exception as err:
            messagebox.showerror("Error", f"Fallo al corregir: {err}")

    tk.Button(frame_critico, text="Aplicar Corrección Autorizada", font=("Arial", 10, "bold"), bg="#D97706", fg="white", cursor="hand2", command=aplicar_correccion_critica).pack(fill="x", ipady=6)

    # ------------------------------------------
    # PESTAÑA 2: VISUALIZACIÓN DE ENTREGAS Y AUDITORÍA
    # ------------------------------------------
    tab_datos = tk.Frame(notebook, bg="white", padx=15, pady=15)
    notebook.add(tab_datos, text="📊 Historial y Auditoría MySQL")

    tk.Label(tab_datos, text="Historial de Entregas Registradas", font=("Arial", 11, "bold"), bg="white", fg="#123B65").pack(anchor="w", pady=(0, 5))

    col_entregas = ("ID", "Productor ID", "Litros", "Estado", "Fecha")
    tabla_entregas = ttk.Treeview(tab_datos, columns=col_entregas, show="headings", height=7)
    for col in col_entregas:
        tabla_entregas.heading(col, text=col)
        tabla_entregas.column(col, width=120, anchor="center")
    tabla_entregas.pack(fill="x", pady=(0, 15))

    tk.Label(tab_datos, text="Historial de Auditoría (Trazabilidad de Cambios)", font=("Arial", 11, "bold"), bg="white", fg="#A31313").pack(anchor="w", pady=(0, 5))

    col_audit = ("ID Audit", "Entrega ID", "Anterior", "Nuevo", "Motivo", "Autorizó", "Fecha")
    tabla_audit = ttk.Treeview(tab_datos, columns=col_audit, show="headings", height=6)
    for col in col_audit:
        tabla_audit.heading(col, text=col)
        tabla_audit.column(col, width=110, anchor="center")
    tabla_audit.pack(fill="x")

    def actualizar_tabla_entregas():
        for item in tabla_entregas.get_children():
            tabla_entregas.delete(item)
        for item in tabla_audit.get_children():
            tabla_audit.delete(item)

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            # Cargar Entregas
            cursor.execute("SELECT EntregaID, ProductorID, LitrosEntregados, Estado, FechaEntrega FROM Entregas")
            for row in cursor.fetchall():
                tabla_entregas.insert("", tk.END, values=row)

            # Cargar Auditoría
            cursor.execute("SELECT AuditoriaID, EntregaID, LitrosAnteriores, LitrosNuevos, MotivoCambio, UsuarioAutoriza, FechaModificacion FROM AuditoriaEntregas")
            for row in cursor.fetchall():
                tabla_audit.insert("", tk.END, values=row)

            cursor.close()
            conn.close()
        except Exception as err:
            print("Error cargando tablas:", err)

    tk.Button(tab_datos, text="🔄 Actualizar Datos desde MySQL", font=("Arial", 10, "bold"), bg="#123B65", fg="white", command=actualizar_tabla_entregas).pack(pady=10)

    # ------------------------------------------
    # PESTAÑA 3: LIQUIDACIÓN QUINCENAL
    # ------------------------------------------
    tab_liquidacion = tk.Frame(notebook, bg="white", padx=20, pady=20)
    notebook.add(tab_liquidacion, text="💰 Liquidación Quincenal")

    tk.Label(tab_liquidacion, text="Calcular Pago Quincenal a Productor", font=("Arial", 13, "bold"), bg="white", fg="#123B65").pack(pady=10)

    tk.Label(tab_liquidacion, text="Ingrese ID del Productor:", font=("Arial", 11), bg="white").pack()
    entry_liq_prod = tk.Entry(tab_liquidacion, font=("Arial", 12), relief="solid", bd=1, justify="center")
    entry_liq_prod.pack(pady=5, ipadx=10, ipady=4)

    lbl_resultado = tk.Label(tab_liquidacion, text="", font=("Arial", 11), bg="#F3F7F4", fg="#123B65", pady=15, padx=20, relief="groove")
    lbl_resultado.pack(fill="x", pady=15)

    def calcular_liquidacion():
        try:
            p_id = int(entry_liq_prod.get())
            conn = obtener_conexion()
            cursor = conn.cursor()

            cursor.execute("SELECT NombreCompleto, Cedula FROM Productores WHERE ProductorID = %s", (p_id,))
            prod = cursor.fetchone()

            if not prod:
                messagebox.showwarning("Aviso", "Productor no encontrado en la Base de Datos.")
                conn.close()
                return

            cursor.execute("SELECT IFNULL(SUM(LitrosEntregados), 0) FROM Entregas WHERE ProductorID = %s", (p_id,))
            total_litros = float(cursor.fetchone()[0])
            tarifa = 0.45
            total_pagar = total_litros * tarifa

            conn.close()

            texto_res = f" Propietario: {prod[0]} (C.I.: {prod[1]})\n" \
                        f" Total Litros Entregados: {total_litros} L\n" \
                        f" Tarifa Base: ${tarifa}/L\n" \
                        f" Total Liquido a Pagar: ${total_pagar:.2f}"
            lbl_resultado.config(text=texto_res)

        except Exception as err:
            messagebox.showerror("Error", "Ingrese un ID numérico válido.")

    tk.Button(tab_liquidacion, text="Calcular Liquidación", font=("Arial", 11, "bold"), bg="#168447", fg="white", cursor="hand2", command=calcular_liquidacion).pack(ipady=6, ipadx=15)

    # Cargar datos iniciales
    actualizar_tabla_entregas()
    dashboard.mainloop()


# ==========================================
# VENTANA DE INICIO DE SESIÓN (LOGIN)
# ==========================================
ventana = tk.Tk()
ventana.title("Leche de Campo - Sistema de Gestión")
ventana.geometry("800x480")
ventana.configure(bg="#F3F7F4")
ventana.resizable(False, False)

# PANEL IZQUIERDO
izquierda = tk.Frame(ventana, bg="#123B65", width=360)
izquierda.pack(side="left", fill="both")
izquierda.pack_propagate(False)

tk.Label(izquierda, text="LECHE DE CAMPO", font=("Arial", 23, "bold"), fg="white", bg="#123B65").pack(pady=(30, 8))
tk.Label(izquierda, text="Sistema de Gestión de Leche", font=("Arial", 11), fg="#DCEAF5", bg="#123B65").pack(pady=(0, 15))

try:
    imagen_original = Image.open("logo_leche.png")
    imagen_original = imagen_original.convert("RGBA")
    imagen_original.thumbnail((290, 240))
    foto = ImageTk.PhotoImage(imagen_original)
    etiqueta_imagen = tk.Label(izquierda, image=foto, bg="#123B65", borderwidth=0)
    etiqueta_imagen.image = foto
    etiqueta_imagen.pack(pady=10)
except Exception:
    tk.Label(izquierda, text="🥛", font=("Arial", 75), fg="white", bg="#123B65").pack(pady=35)

tk.Label(izquierda, text="Pura • Natural • Fresca", font=("Arial", 12, "bold"), fg="#B8E986", bg="#123B65").pack(pady=15)
tk.Label(izquierda, text="Producción y comercialización", font=("Arial", 10), fg="white", bg="#123B65").pack(side="bottom", pady=20)

# PANEL DERECHO
derecha = tk.Frame(ventana, bg="white", padx=40, pady=30)
derecha.pack(side="right", fill="both", expand=True)

tk.Label(derecha, text="Bienvenido", font=("Arial", 25, "bold"), bg="white", fg="#123B65").pack(pady=(35, 5))
tk.Label(derecha, text="Ingresa tus datos para continuar", font=("Arial", 10), bg="white", fg="#667788").pack(pady=(0, 25))

tk.Label(derecha, text="Usuario", font=("Arial", 11, "bold"), bg="white", fg="#263746").pack(anchor="w")
usuario = tk.Entry(derecha, font=("Arial", 12), relief="solid", bd=1)
usuario.pack(fill="x", ipady=7, pady=(6, 15))

tk.Label(derecha, text="Contraseña", font=("Arial", 11, "bold"), bg="white", fg="#263746").pack(anchor="w")
clave = tk.Entry(derecha, font=("Arial", 12), show="*", relief="solid", bd=1)
clave.pack(fill="x", ipady=7, pady=(6, 20))

def ingresar():
    nombre_usuario = usuario.get().strip()
    contrasena = clave.get()

    if nombre_usuario == "admin" and contrasena == "1234":
        messagebox.showinfo("Acceso correcto", "¡Bienvenido a Leche de Campo!")
        abrir_sistema_principal(ventana)
    else:
        messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")

tk.Button(
    derecha, text="INGRESAR", font=("Arial", 12, "bold"), bg="#168447", fg="white",
    activebackground="#116B39", activeforeground="white", relief="flat", cursor="hand2", command=ingresar
).pack(fill="x", ipady=9, pady=5)

ventana.bind("<Return>", lambda evento: ingresar())
usuario.focus_set()
ventana.mainloop()