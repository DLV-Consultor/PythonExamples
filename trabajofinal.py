# region Mislibrerias
from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk
import mysql.connector
import matplotlib.pyplot as plt    
import random
import re
# endregion
# region MisFunciones
#Conecto a la base que voy a usar para todas las operaciones
def conexion_db():
    try:
        mibase = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="riesgos_dbv2"
    )   
        return mibase
    except:
        showerror("Error",f"Error al conectarse a la base de datos \n^{Exception.mro}" )
#Creo la base de datos sobre la que voy a registrar todo, state=isabled en menu en caso de no necesitar
def crear_db():
    try:
        mibase = mysql.connector.connect(
        host="localhost",
        user="root",
        password="")  
        micursor = mibase.cursor()
        micursor.execute("CREATE DATABASE riesgos_dbv2")
    except:
        showerror("Error",f"Error al crear base de datos \n^{Exception.mro}" )
#Genero la tablas maestras state=isabled en menu en caso de no necesitar
def crear_tablas():
    try:
        mibase = conexion_db()
        micursor = mibase.cursor()
        micursor.execute("CREATE TABLE compania(id int(4) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                    "nombre_cia VARCHAR(60) COLLATE utf8_spanish2_ci NOT NULL)")
        micursor.execute("CREATE TABLE activo(id int(4) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                    "nombre_act VARCHAR(160) COLLATE utf8_spanish2_ci NOT NULL)")
        micursor.execute("CREATE TABLE vulne(id int(4) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                    "nombre_vul VARCHAR(100) COLLATE utf8_spanish2_ci NOT NULL)")
        micursor.execute("CREATE TABLE amenazas(id int(4) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                    "nombre_ame VARCHAR(100) COLLATE utf8_spanish2_ci NOT NULL)")
        micursor.execute("CREATE TABLE relaciones(id_rel int(5) NOT NULL PRIMARY KEY AUTO_INCREMENT,id_act INT(4),"
                    "nombre_act VARCHAR(160),id_vul INT(4), nombre_vul VARCHAR(100),id_ame INT(4),"
                    "nombre_ame VARCHAR(100) COLLATE utf8_spanish2_ci NOT NULL)")
        micursor.execute("CREATE TABLE riesgos(id int(5) NOT NULL PRIMARY KEY AUTO_INCREMENT, nombre_cia VARCHAR(60),"
                    "nombre_act VARCHAR(160), nombre_vul VARCHAR(100), nombre_ame VARCHAR(100), probabilidad int(1),"
                    "intensidad int(1), riesgo int(1) COLLATE utf8_spanish2_ci NOT NULL)")
    except:
        showerror("Error",f"Error al crear tablas \n^{Exception.mro}" )
#Para widget y otros dar de alta todos los maestros
def alta_baja(tabla,tipo):
   for widget in main.winfo_children():
       widget.grid_remove() # remuevo todos los widget de main para que quede pantalla limpia
   if tipo=="alta":
        main.campo_lab = Label(main, text=f"Ingrese el nombre de {tabla} a dar de {tipo}:  ",
                               font=("Arial", 12, "bold"))
        main.campo_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)
        main.campo_e = Entry(main,width=60, textvariable= entrada)
        main.campo_e.grid(row=1, column=0, sticky=W, padx=20, pady=0)
   else:
       combo = ttk.Combobox(main,state="readonly",height=20,width=80, textvariable= entrada)
       if tabla=="activo":
           sql="SELECT * FROM activo ORDER BY nombre_act"
       elif tabla=="vulnerabilidades":
           sql="SELECT * FROM vulne ORDER BY nombre_vul"
       elif tabla =="amenazas":
           sql="SELECT * FROM amenazas ORDER BY nombre_ame"
       elif tabla =="compania":
           sql="SELECT * FROM compania ORDER BY nombre_cia"
       conexion = conexion_db()
       micursor = conexion.cursor()
       micursor.execute(sql)
       resultado = micursor.fetchall()
       main.campo_lab = Label(main, text=f"Ingrese el nombre de {tabla} a dar de {tipo}:  ",
                               font=("Arial", 12, "bold"))
       main.campo_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)
       valores=[]
       for x in resultado:
           valores+=[x[1]]
       combo['values'] = valores
       combo.grid(row=1, column=0, padx=20, pady=0)     
   main.bto_guardar = Button(main,text="Guardar", command= lambda: guardar_f(tabla,tipo, (entrada.get(),)) 
                                                                             if valida_vacio.match(entrada.get())
                                                                             else showerror("Gestion de riesgos 1.0","Entrada no puede ser vacia",parent= main) 
                                                                             )
   main.bto_guardar.grid(row=1,column=2) #ejecuta funcion guardar_f para ABM de base de datos
#widget y Query para consulta de información de maestros  
def consulta(tabla):
    for widget in main.winfo_children():
        widget.grid_remove() #remuevo todos los widget de main para que quede pantalla limpia
    main.campo_lab = Label(main, text=f" Consulta de {tabla}:  ",
                               font=("Arial", 12, "bold"))
    main.campo_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)
    tree = ttk.Treeview(main)
    tree["columns"] = ("nombre",)
    tree.column("#0", width=50, minwidth=50, anchor=W)
    tree.column("nombre", width=450, minwidth=80, anchor=W)
    tree.heading("#0",text="id")
    tree.heading("nombre",text="Nombre")       
    tree.grid(row=1,column=0, columnspan=20,padx=20, pady=0,sticky=W)
    conexion = conexion_db()
    micursor = conexion.cursor()
    sql=f"SELECT * FROM {tabla} ORDER BY 2"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:  
        tree.insert(
            "", "end", text= x[0], values= (x[1],))
# Altas de relaciones entre maestros    
def alta_relacion():
    for widget in main.winfo_children():
        widget.grid_remove() #remuevo todos los widget de main para que quede pantalla limpia
    conexion = conexion_db()
    micursor = conexion.cursor()
    main.ref_lab = Label(main, text="Alta de relación:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)    
    tree_a = ttk.Treeview(main, selectmode="browse")
    tree_a["columns"] = ("nombre",)
    tree_a.column("#0", width=50, minwidth=30, stretch=True)
    tree_a.column("nombre", width=300, minwidth=80, anchor=W)
    tree_a.heading("#0",text="id")
    tree_a.heading("nombre",text="Activo")       
    tree_a.grid(column=0, row=1,padx=10, pady=0,sticky=W)
    sql="SELECT * FROM activo ORDER BY nombre_act"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_a.insert(
            "", "end", text= x[0], values=(x[1],))
    primero = tree_a.get_children()[0] #Doy foco a primer elemento con ayuda de copilot
    tree_a.selection_set(primero)      #Doy foco a primer elemento con ayuda de copilot
    tree_a.focus(primero)              #Doy foco a primer elemento con ayuda de copilot
        
    tree_v = ttk.Treeview(main, selectmode="browse")
    tree_v["columns"] = ("nombre",)
    tree_v.column("#0", width=50, minwidth=30, anchor=W)
    tree_v.column("nombre", width=400, minwidth=80, anchor=W)
    tree_v.heading("#0",text="id")
    tree_v.heading("nombre",text="Vulnerab.")       
    tree_v.grid(column=1, row=1)
    sql="SELECT * FROM vulne ORDER BY nombre_vul"
    micursor.execute(sql) #
    resultado = micursor.fetchall()
    for x in resultado:
        tree_v.insert(
            "", "end", text= x[0], values=(x[1],))
    primero = tree_v.get_children()[0] #Doy foco a primer elemento con ayuda de copilot
    tree_v.selection_set(primero)      #Doy foco a primer elemento con ayuda de copilot
    tree_v.focus(primero)              #Doy foco a primer elemento con ayuda de copilot
        
    tree_am = ttk.Treeview(main, selectmode="browse")
    tree_am["columns"] = ("nombre",)
    tree_am.column("#0", width=50, minwidth=30, anchor=W)
    tree_am.column("nombre", width=400, minwidth=80, anchor=W)
    tree_am.heading("#0",text="id")
    tree_am.heading("nombre",text="Amenaza")       
    tree_am.grid(column=2, row=1,padx=10, pady=0,sticky=W)
    sql="SELECT * FROM amenazas ORDER BY nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_am.insert(
            "", "end", text= x[0], values=(x[1],))
    primero = tree_am.get_children()[0] #Doy foco a primer elemento con ayuda de copilot
    tree_am.selection_set(primero)      #Doy foco a primer elemento con ayuda de copilot
    tree_am.focus(primero)              #Doy foco a primer elemento con ayuda de copilot     
    main.bto_guardar = Button(main,text="Guardar", command= lambda: guardar_f("relacion","alta",(
                                                                        tree_am.item(tree_am.focus(),"values")[0],tree_am.item(tree_am.focus(),"text"),
                                                                               tree_v.item(tree_v.focus(),"values")[0],tree_v.item(tree_v.focus(),"text"),
                                                                               tree_a.item(tree_a.focus(),"values")[0],tree_a.item(tree_a.focus(),"text")
                                                                        )))
    main.bto_guardar.grid(column=3,row=1) #ejecuta funcion guardar_f para ABM de base de datos
#Bajas de relaciones entre maestros    
def baja_relacion():
    for widget in main.winfo_children():
        widget.grid_remove() #remuevo todos los widget de main para que quede pantalla limpia
    conexion = conexion_db()
    micursor = conexion.cursor()
    main.ref_lab = Label(main, text="Baja de relación:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)        
    tree_r = ttk.Treeview(main, selectmode="browse")
    tree_r["columns"] = ("Activo","Vulnerabilidad", "Amenaza")
    tree_r.column("#0", width=50, minwidth=30, stretch=True)
    tree_r.column("Activo", width=450, minwidth=80, anchor=W)
    tree_r.column("Vulnerabilidad", width=400, minwidth=80, anchor=W)
    tree_r.column("Amenaza", width=400, minwidth=80, anchor=W)
    tree_r.heading("#0",text="id")
    tree_r.heading("Activo",text="Activo") 
    tree_r.heading("Vulnerabilidad",text="Vulnerabilidad")
    tree_r.heading("Amenaza",text="Amenaza")          
    tree_r.grid(column=0, row=1,padx=20, pady=0,sticky=W)
    sql="SELECT id_rel,nombre_act,nombre_vul,nombre_ame FROM relaciones ORDER BY nombre_act,nombre_vul,nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_r.insert(
            "", "end", text= x[0], values=(x[1],x[2],x[3]))
    primero = tree_r.get_children()[0] #con ayuda de copilot
    tree_r.selection_set(primero)      #con ayuda de copilot
    tree_r.focus(primero)              #con ayuda de copilot    
    main.bto_guardar = Button(main,text="Guardar", command= lambda: guardar_f("relacion","baja",(tree_r.item(tree_r.focus(),"text"
                                                                                                            ),)))
    main.bto_guardar.grid(row=2,column=0, sticky=E, padx=20, pady=5) #ejecuta funcion guardar_f para ABM de base de datos
#Consultas de relaciones entre maestros
def consulta_relacion():
    for widget in main.winfo_children():
        widget.grid_remove()
    conexion = conexion_db()
    micursor = conexion.cursor()
    main.ref_lab = Label(main, text="Consulta de relación:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)        
    tree_c = ttk.Treeview(main, selectmode="browse")
    tree_c["columns"] = ("Activo","Vulnerabilidad", "Amenaza")
    tree_c.column("#0", width=50, minwidth=30, stretch=True)
    tree_c.column("Activo", width=450, minwidth=80, anchor=W)
    tree_c.column("Vulnerabilidad", width=400, minwidth=80, anchor=W)
    tree_c.column("Amenaza", width=400, minwidth=80, anchor=W)
    tree_c.heading("#0",text="id")
    tree_c.heading("Activo",text="Activo") 
    tree_c.heading("Vulnerabilidad",text="Vulnerabilidad")
    tree_c.heading("Amenaza",text="Amenaza")          
    tree_c.grid(column=0, row=1,padx=20, pady=0,sticky=W)
    sql="SELECT id_rel,nombre_act,nombre_vul,nombre_ame FROM relaciones ORDER BY nombre_act,nombre_vul,nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_c.insert(
            "", "end", text= x[0], values=(x[1],x[2],x[3]))
# Altas de riesgos  
def alta_riesgo():
    for widget in main.winfo_children():
        widget.grid_remove() # remuevo todos los widget de main para que quede pantalla limpia
    conexion = conexion_db()
    micursor = conexion.cursor()
    main.ref_lab = Label(main, text="Alta de riesgo:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)    
    main.inte_lab = Label(main, text="Probabilidad 1 a 3: ",font=("bold"))
    main.inte_lab.grid(row=2, column=0, sticky=W, padx=10,pady=10) 
    main.inte_e = Entry(main,width=2, textvariable= entrada_inte)
    main.inte_e.grid(row=2, column=1, sticky=W, padx=10,pady=10)
    main.prob_lab = Label(main, text="Intensidad  1 a 3: ",font=("bold"))
    main.prob_lab.grid(row=3, column=0, sticky=W, padx=10,pady=10) 
    main.prob_e = Entry(main,width=2, textvariable= entrada_prob)
    main.prob_e.grid(row=3, column=1, sticky=W, padx=10,pady=10)    
    tree_e = ttk.Treeview(main, selectmode="browse")
    tree_e["columns"] = ("nombre",)
    tree_e.column("#0", width=50, minwidth=30, stretch=True)
    tree_e.column("nombre", width=100, minwidth=80, anchor=W)
    tree_e.heading("#0",text="id")
    tree_e.heading("nombre",text="Empresa")       
    tree_e.grid(row=1,column=0, padx=10,pady=10)
    sql="SELECT * FROM compania ORDER BY nombre_cia"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_e.insert(
            "", "end", text= x[0], values=x[1])
    primero = tree_e.get_children()[0] #con ayuda de copilot
    tree_e.selection_set(primero)      #con ayuda de copilot
    tree_e.focus(primero)              #con ayuda de copilot    
    tree_r = ttk.Treeview(main, selectmode="browse")
    tree_r["columns"] = ("nombre_act","nombre_vul","nombre_ame")
    tree_r.column("#0", width=50, minwidth=30, anchor=W)
    tree_r.column("nombre_act", width=300, minwidth=80, anchor=W)
    tree_r.column("nombre_vul", width=300, minwidth=80, anchor=W)
    tree_r.column("nombre_ame", width=300, minwidth=80, anchor=W)
    tree_r.heading("#0",text="id")
    tree_r.heading("nombre_act",text="Activo")       
    tree_r.heading("nombre_vul",text="Vulnerabilidad")
    tree_r.heading("nombre_ame",text="Amenaza")
    tree_r.grid(row=1,column=1,pady=10)
    sql="SELECT id_rel, nombre_act, nombre_vul, nombre_ame FROM relaciones ORDER BY nombre_act,nombre_vul,nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_r.insert(
            "", "end", text= x[0], values=(x[1],x[2],x[3]))
    primero = tree_r.get_children()[0] #con ayuda de copilot
    tree_r.selection_set(primero)      #con ayuda de copilot
    tree_r.focus(primero)              #con ayuda de copilot      
    main.bto_guardar = Button(main,text="Guardar",
                              command= lambda: guardar_f("riesgo","alta",(
                                                                        tree_e.item(tree_e.focus(),"values")[0],
                                                                        tree_r.item(tree_r.focus(),"values")[0],
                                                                        tree_r.item(tree_r.focus(),"values")[1],
                                                                        tree_r.item(tree_r.focus(),"values")[2],
                                                                        entrada_inte.get(),entrada_prob.get(),
                                                                        int(entrada_inte.get())*int(entrada_prob.get()))
                                                         )
                              if valida_numero.match(entrada_prob.get()) and valida_numero.match(entrada_inte.get()) else
                              showerror("Gestion de riesgos 1.0","Valores de Probabilidad e intensidad no validos",parent= main)
                              ) #ejecuta funcion guardar_f para ABM de base de datos
    main.bto_guardar.grid(row=4,column=1, sticky=W)
#Bajas de riesgos 
def baja_riesgo():
    for widget in main.winfo_children():
        widget.grid_remove() # remuevo todos los widget de main para que quede pantalla limpia
    conexion = conexion_db()
    micursor = conexion.cursor()
    main.ref_lab = Label(main, text="Baja de riesgo:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)        
    tree_rb = ttk.Treeview(main, selectmode="browse")
    tree_rb["columns"] = ("Empresa","Activo","Vulnerabilidad", "Amenaza", "Intensidad", "Probabilidad","Riesgo")
    tree_rb.column("#0", width=5, minwidth=5, stretch=True)
    tree_rb.column("Empresa", width=50, minwidth=80, anchor=W)
    tree_rb.column("Activo", width=300, minwidth=80, anchor=W)
    tree_rb.column("Vulnerabilidad", width=300, minwidth=80, anchor=W)
    tree_rb.column("Amenaza", width=300, minwidth=80, anchor=W)
    tree_rb.column("Intensidad", width=100, minwidth=40, anchor=CENTER)
    tree_rb.column("Probabilidad", width=120, minwidth=40, anchor=CENTER)
    tree_rb.column("Riesgo", width=100, minwidth=40, anchor=CENTER)
    tree_rb.heading("#0",text="id")
    tree_rb.heading("Empresa",text="Empresa") 
    tree_rb.heading("Activo",text="Activo") 
    tree_rb.heading("Vulnerabilidad",text="Vulnerabilidad")
    tree_rb.heading("Amenaza",text="Amenaza")
    tree_rb.heading("Intensidad",text="Intensidad")
    tree_rb.heading("Probabilidad",text="Probabilidad")
    tree_rb.heading("Riesgo",text="Riesgo")          
    tree_rb.grid(row=1, column=0, padx=10)
    sql="SELECT id,nombre_cia,nombre_act,nombre_vul,nombre_ame,probabilidad,intensidad,riesgo FROM riesgos ORDER BY nombre_cia,nombre_act,nombre_vul,nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_rb.insert(
            "", "end", text= x[0], values=(x[1],x[2],x[3],x[4],x[5],x[6],x[7]))
    primero = tree_rb.get_children()[0] #con ayuda de copilot
    tree_rb.selection_set(primero)      #con ayuda de copilot
    tree_rb.focus(primero)              #con ayuda de copilot    
    main.bto_guardar = Button(main,text="Guardar", command= lambda: guardar_f("riesgos","baja",(tree_rb.item(tree_rb.focus(),"text"
                                                                      ),)))
    main.bto_guardar.grid(row=2, column=0, sticky=E,padx=10,pady=10) #ejecuta funcion guardar_f para ABM de base de datos
#Consultas de riesgos
def consulta_riesgo():
    for widget in main.winfo_children():
        widget.grid_remove() # remuevo todos los widget de main para que quede pantalla limpia
    conexion = conexion_db()
    micursor = conexion.cursor()   
    main.ref_lab = Label(main, text="Consulta de riesgo:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)       
    tree_co = ttk.Treeview(main, selectmode="browse")
    tree_co["columns"] = ("Empresa","Activo","Vulnerabilidad", "Amenaza", "Intensidad", "Probabilidad","Riesgo")
    tree_co.column("#0", width=5, minwidth=5, stretch=True)
    tree_co.column("Empresa", width=50, minwidth=80, anchor=W)
    tree_co.column("Activo", width=300, minwidth=80, anchor=W)
    tree_co.column("Vulnerabilidad", width=300, minwidth=80, anchor=W)
    tree_co.column("Amenaza", width=300, minwidth=80, anchor=W)
    tree_co.column("Intensidad", width=100, minwidth=40, anchor=CENTER)
    tree_co.column("Probabilidad", width=120, minwidth=40, anchor=CENTER)
    tree_co.column("Riesgo", width=100, minwidth=40, anchor=CENTER)
    tree_co.heading("#0",text="id")
    tree_co.heading("Empresa",text="Empresa") 
    tree_co.heading("Activo",text="Activo") 
    tree_co.heading("Vulnerabilidad",text="Vulnerabilidad")
    tree_co.heading("Amenaza",text="Amenaza")
    tree_co.heading("Intensidad",text="Intensidad")
    tree_co.heading("Probabilidad",text="Probabilidad")
    tree_co.heading("Riesgo",text="Riesgo")   
    tree_co.grid(row=1, column=0, padx=10)                
    sql="SELECT id,nombre_cia,nombre_act,nombre_vul,nombre_ame,probabilidad,intensidad,riesgo FROM riesgos ORDER BY nombre_cia,nombre_act,nombre_vul,nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_co.insert(
            "", "end", text= x[0], values=(x[1],x[2],x[3],x[4],x[5],x[6],x[7]))
#Modfifica Riesgos
def modifica_riesgo():
    for widget in main.winfo_children():
        widget.grid_remove() # remuevo todos los widget de main para que quede pantalla limpia
    conexion = conexion_db()
    micursor = conexion.cursor()
    main.ref_lab = Label(main, text="Modificación de riesgo:",
                               font=("Arial", 12, "bold"))
    main.ref_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10) 
    main.inte_lab = Label(main, text="\t\t\t\t Intensidad  1 a 3: ",font=("bold"))
    main.inte_lab.grid(row=2, column=0, sticky=W, padx=10,pady=10) 
    main.inte_e = Entry(main,width=2, textvariable= entrada_inte)
    main.inte_e.grid(row=2, column=0, padx=10,pady=10)
    main.prob_lab = Label(main, text="\t\t\t\t Probabilidad 1 a 3: ",font=("bold"))
    main.prob_lab.grid(row=3, column=0, sticky=W, padx=10,pady=10) 
    main.prob_e = Entry(main,width=2, textvariable= entrada_prob,)
    main.prob_e.grid(row=3, column=0, padx=10,pady=10)       
    tree_co = ttk.Treeview(main, selectmode="browse")
    tree_co["columns"] = ("Empresa","Activo","Vulnerabilidad", "Amenaza", "Intensidad", "Probabilidad","Riesgo")
    tree_co.column("#0", width=5, minwidth=5, stretch=True)
    tree_co.column("Empresa", width=50, minwidth=80, anchor=W)
    tree_co.column("Activo", width=300, minwidth=80, anchor=W)
    tree_co.column("Vulnerabilidad", width=300, minwidth=80, anchor=W)
    tree_co.column("Amenaza", width=300, minwidth=80, anchor=W)
    tree_co.column("Intensidad", width=100, minwidth=40, anchor=CENTER)
    tree_co.column("Probabilidad", width=120, minwidth=40, anchor=CENTER)
    tree_co.column("Riesgo", width=100, minwidth=40, anchor=CENTER)
    tree_co.heading("#0",text="id")
    tree_co.heading("Empresa",text="Empresa") 
    tree_co.heading("Activo",text="Activo") 
    tree_co.heading("Vulnerabilidad",text="Vulnerabilidad")
    tree_co.heading("Amenaza",text="Amenaza")
    tree_co.heading("Intensidad",text="Intensidad")
    tree_co.heading("Probabilidad",text="Probabilidad")
    tree_co.heading("Riesgo",text="Riesgo")          
    tree_co.grid(row=1,column=0, padx=10,pady=10)
    sql="SELECT id,nombre_cia,nombre_act,nombre_vul,nombre_ame,probabilidad,intensidad,riesgo FROM riesgos ORDER BY nombre_cia,nombre_act,nombre_vul,nombre_ame"
    micursor.execute(sql)
    resultado = micursor.fetchall()
    for x in resultado:
        tree_co.insert(
            "", "end", text= x[0], values=(x[1],x[2],x[3],x[4],x[5],x[6],x[7]))
    primero = tree_co.get_children()[0] #con ayuda de copilot
    tree_co.selection_set(primero)      #con ayuda de copilot
    tree_co.focus(primero)              #con ayuda de copilot
    main.bto_guardar = Button(main,text="Guardar", 
                              command= lambda: guardar_f("riesgos","modificar",(entrada_inte.get(),
                                                                                entrada_prob.get(),
                                                                                int(entrada_inte.get())*int(entrada_prob.get()),
                                                                                tree_co.item(tree_co.focus(),"text"))
                                                         )
                              if valida_numero.match(entrada_prob.get()) and valida_numero.match(entrada_inte.get()) else 
                              showerror("Gestion de riesgos 1.0","Valores de Probabilidad e intensidad no validos",parent= main)
                              )#ejecuta funcion guardar_f para ABM de base de datos
    main.bto_guardar.grid(row=4,column=0)       
#Filtrar riesgo por compañia para graficar
def filtra_grafico():
    for widget in main.winfo_children():
        widget.grid_remove() # remuevo todos los widget de main para que quede pantalla limpia
    combo = ttk.Combobox(main,state="readonly",height=20,width=80, textvariable= entrada)
    sql="SELECT * FROM compania ORDER BY nombre_cia"
    conexion = conexion_db()
    micursor = conexion.cursor()
    micursor.execute(sql)
    resultado = micursor.fetchall()
    main.campo_lab = Label(main, text=f" Ingrese el nombre de compañia:  ",
                               font=("Arial", 12, "bold"))
    main.campo_lab.grid(row=0, column=0, sticky=W, padx=10,pady=10)
    valores=[]
    for x in resultado:
       valores+=[x[1]]
    combo['values'] = valores
    combo.grid(row=2, column=0, padx=20, pady=10)
    main.bto_guardar = Button(main,text="Consultar", command= lambda: grafico(entrada.get()))
    main.bto_guardar.grid(column=1,row=2)
#Filtra datos en base de dato y grafica lo que me traigo 
def grafico(compania):
    print(compania)
    ingresar=(compania,)
    conexion = conexion_db()
    micursor = conexion.cursor()
    sql="SELECT probabilidad,intensidad FROM riesgos WHERE nombre_cia = %s"
    micursor.execute(sql,ingresar)
    resultado = micursor.fetchall()
    X_prob,y_int=[],[]
    for x in resultado:
        X_prob.append(x[0]-0.5+random.uniform(-0.3, 0.3))
        y_int.append(x[1]-0.5+random.uniform(-0.3, 0.3))
    print(X_prob,y_int)  
    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(6, 6),)
    # Rango de valores para los ejes
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.scatter(X_prob,y_int, colorizer="red", s=80, alpha=0.5)
    # Dibujar ejes X e Y en el centro
    ax.axhline(0, color='black', linewidth=1)  # Eje X
    ax.axvline(0, color='black', linewidth=1)  # Eje Y
    # Activar cuadrícula
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.text(0.5, 0.5, 'I', fontsize=12, color='green')
    ax.text(1.5, 0.5, 'II', fontsize=12, color='green')
    ax.text(2.5, 0.5, 'III', fontsize=12, color='yellow')
    ax.text(0.5, 1.5, 'IV', fontsize=12, color='green')
    ax.text(1.5, 1.5, 'V', fontsize=12, color='yellow')
    ax.text(2.5, 1.5, 'VI', fontsize=12, color='red')
    ax.text(0.5, 2.5, 'VII', fontsize=12, color='yellow')
    ax.text(1.5, 2.5, 'VIII', fontsize=12, color='red')
    ax.text(2.5, 2.5, 'IX', fontsize=12, color='red') 
    ax.set_title(f'Matriz de Riesgos de {ingresar[0]}')
    fig.canvas.manager.set_window_title("Matriz de Riesgos")
    plt.show()
    # Mostrar
#Ejecuta en base de datos ABM  
def guardar_f(tabla,tipo,rela=()): 
    conexion = conexion_db()
    micursor = conexion.cursor()
    ingresar=(rela)
    try:
        print(type(ingresar))
        print(ingresar)
        if askyesno("Actualización de Datos Maestros", "Desea dar {0} en {1} ?".format(tipo,tabla)):
            if tipo=="alta": #podria simplicar en un solo Query si modificara el nombre de los campos de las tablas, no se si es buena practica..
                if tabla=="compania":
                    sql = "INSERT INTO compania (nombre_cia) VALUES (%s)"
                elif tabla=="amenazas":
                    sql = "INSERT INTO amenazas (nombre_ame) VALUES (%s)"
                elif tabla=="activo":
                    sql = "INSERT INTO activo (nombre_act) VALUES (%s)"
                elif tabla=="vulnerabilidades":
                    sql = "INSERT INTO vulne (nombre_vul) VALUES (%s)"
                elif tabla=="relacion":
                     sql ="INSERT INTO relaciones (nombre_ame,id_ame,nombre_vul,id_vul,nombre_act,id_act) VALUES (%s,%s,%s,%s,%s,%s)"
                elif tabla=="riesgo":
                    sql ="INSERT INTO riesgos (nombre_cia,nombre_act,nombre_vul,nombre_ame,intensidad,probabilidad,riesgo) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            elif tipo=="baja":
                if tabla=="compania":
                    sql = "DELETE FROM compania WHERE nombre_cia = (%s)"
                elif tabla=="amenazas":
                    sql = "DELETE FROM amenazas WHERE nombre_ame= (%s)"
                elif tabla=="activo":
                    sql = "DELETE FROM activo WHERE nombre_act = (%s)"
                elif tabla=="vulnerabilidades":
                    sql = "DELETE FROM vulne WHERE nombre_vul = (%s)"  
                elif tabla=="relacion":
                    sql = "DELETE FROM relaciones WHERE id_rel = (%s)"
                elif tabla=="riesgos":
                    sql = "DELETE FROM riesgos WHERE id = (%s)"
            elif tipo=="modificar":
                if tabla=="riesgos":
                    sql = "UPDATE riesgos SET probabilidad=%s, intensidad=%s, riesgo=%s  WHERE id = (%s)"
            micursor.execute(sql,ingresar) 
            conexion.commit()
            entrada.set("")
            showinfo("Gestion de riesgos 1.0","Se ejecuto la operación")
    except:
        showerror("Error",f"Error al ejecutar base de datos vueva a intentarlo \n^{Exception.mro}" )   
# endregion   
# region interfaz de usuario 
main = Tk()

#variables que luego voy a usar para extraer los datos ingresados en widgets
entrada= StringVar()
entrada_inte= StringVar()
entrada_prob= StringVar()
valida_numero = re.compile(r'^[123]$')
valida_vacio= re.compile(r'.+')

#configuro la pantalla de tkinter y asigno titulo e icono de la aplicación
main.title("Gestion de Riesgos 1.0") 
logo = "iconoapp.ico"
main.iconbitmap(False,logo)
main.geometry("1400x600",)

#doy estilo a los Treeview que voy a utilizar
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"),background="#14212D",foreground="#FEFEFF")

# Creo menus archivo,riesgos, maestros, Acerca de y todos sus submenus, llamando a funciones
menubar = Menu(main)

menu_archivo = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Archivo", menu=menu_archivo)
menu_archivo.add_command(label="Crear Base de Datos", command=lambda: crear_db()) #, state=DISABLED
menu_archivo.add_command(label="Crear tablas", command=lambda: crear_tablas())    #, state=DISABLED
menu_archivo.add_command(label="Salir", command= lambda: main.quit() if askyesno("Gestion de riesgos 1.0", 
                                                                               "Desea Salir del sistema?") else print("o"))

menu_riesgos = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Riesgos", menu=menu_riesgos)
menu_riesgos.add_command(label="Alta", command= lambda:alta_riesgo())
menu_riesgos.add_command(label="Baja", command= lambda:baja_riesgo())
menu_riesgos.add_command(label="Consulta", command= lambda:consulta_riesgo())
menu_riesgos.add_command(label="Modificación", command= lambda:modifica_riesgo())
menu_riesgos.add_separator()
menu_riesgos.add_command(label="Grafico", command= lambda:filtra_grafico())
menu_maestros = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Maestros", menu=menu_maestros)

submenu_asset = Menu(menu_maestros, tearoff=0)
menu_maestros.add_cascade(label="Activo", menu=submenu_asset)
submenu_asset.add_command(label="Alta", command=lambda: alta_baja("activo","alta"))
submenu_asset.add_command(label="Baja", command=lambda: alta_baja("activo","baja"))
submenu_asset.add_command(label="Consulta", command=lambda: consulta("activo"))

submenu_amenazas = Menu(menu_maestros, tearoff=0)
menu_maestros.add_cascade(label="Amenazas", menu=submenu_amenazas)
submenu_amenazas.add_command(label="Alta", command=lambda: alta_baja("amenazas","alta"))
submenu_amenazas.add_command(label="Baja", command=lambda: alta_baja("amenazas","baja"))
submenu_amenazas.add_command(label="Consulta", command=lambda: consulta("amenazas"))

submenu_compañia = Menu(menu_maestros, tearoff=0)
menu_maestros.add_cascade(label="Compañias", menu=submenu_compañia)
submenu_compañia.add_command(label="Alta", command=lambda: alta_baja("compania","alta"))
submenu_compañia.add_command(label="Baja", command=lambda: alta_baja("compania","baja"))
submenu_compañia.add_command(label="Consulta", command=lambda: consulta("compania"))

submenu_vulnera = Menu(menu_maestros, tearoff=0)
menu_maestros.add_cascade(label="Vulnerabilidades", menu=submenu_vulnera)
submenu_vulnera.add_command(label="Alta", command=lambda: alta_baja("vulnerabilidades","alta"))
submenu_vulnera.add_command(label="Baja", command=lambda: alta_baja("vulnerabilidades","baja"))
submenu_vulnera.add_command(label="Consulta", command=lambda: consulta("vulne"))

submenu_relaciones = Menu(menu_maestros, tearoff=0)
menu_maestros.add_separator()
menu_maestros.add_cascade(label="Relaciones", menu=submenu_relaciones)
submenu_relaciones.add_command(label="Alta", command= lambda: alta_relacion())
submenu_relaciones.add_command(label="Baja", command=lambda:baja_relacion())
submenu_relaciones.add_command(label="Consulta", command=lambda:consulta_relacion())
menu_help = Menu(menubar, tearoff=0) 
menubar.add_cascade(label="Acerca de", menu=menu_help)
menu_help.add_command(label="?", command=lambda: showinfo("Gestion de riesgos 1.0",
                                                                     "Gestión de riesgos\nVersion 1.0\nby DALV\n2026 ",
                                                                     icon="info",parent= main
                                                                    ) )
main.config(menu=menubar)

main.mainloop()
# endregion