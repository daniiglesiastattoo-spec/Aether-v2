from fpdf import FPDF
import glob

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AETHER - Arquitectura y Esquema', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Using latin-1 encoding for FPDF default fonts
        self.multi_cell(0, 6, body.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(4)

pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', '', 11)

intro = "AETHER es un sistema de IA autonomo para Android, compuesto por modulos especializados que se comunican entre si. A continuacion se presenta el desglose de su arquitectura:"
pdf.multi_cell(0, 6, intro)
pdf.ln(5)

# Module 1
pdf.chapter_title('1. AETHER CORE (Nucleo de Control)')
pdf.chapter_body('Orquesta todo el sistema. Funciona en segundo plano (AetherCoreService) y mantiene el "latido" continuo del agente. Supervisa el estado fisico del dispositivo (bateria, memoria, red), el nivel de activacion y gestiona las prioridades (StateRepository).')

# Module 2
pdf.chapter_title('2. MIND (Procesamiento Cognitivo)')
pdf.chapter_body('Este modulo (LocalLlmEngine, GeminiService, GroqService) toma decisiones, comprende intenciones y genera lenguaje. Integra procesamiento local para privacidad e inmediatez, y opciones en la nube para razonamiento complejo.')

# Module 3
pdf.chapter_title('3. VISION (Percepcion Visual)')
pdf.chapter_body('A traves de VisionManager y LocalVisionEngine, AETHER puede ver y analizar su entorno utilizando la camara del dispositivo, entendiendo estimulos visuales en tiempo real.')

# Module 4
pdf.chapter_title('4. EVOLUTION (Memoria y Autorreflexion)')
pdf.chapter_body('Modulo avanzado (ReflexionEngine, EvolutionScanner) que permite a AETHER mejorar con el tiempo. Reflexiona sobre interacciones pasadas y propone evoluciones en parametros, codigo, arquitectura y uso de memoria.')

# Module 5
pdf.chapter_title('5. VERITAS (Base de Conocimiento)')
pdf.chapter_body('LocalKnowledgeLibrary actua como la memoria a largo plazo verificada. Contiene hechos, preferencias del usuario e historial de estados (AppDatabase).')

# Module 6
pdf.chapter_title('6. AGENTS (Ejecucion de Tareas)')
pdf.chapter_body('Modulos de accion con el entorno exterior, que ejecutan codigo local (PythonBridgeManager), sintetizan o escuchan voz (VoiceManager) e interactuan con la interfaz de usuario de Android.')

pdf.add_page()
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'Esquema Visual de AETHER:', 0, 1, 'C')

try:
    img_path = glob.glob('app/src/main/res/drawable/aether_schematic_*.jpg')[0]
    pdf.image(img_path, x=20, w=170)
except Exception as e:
    pdf.cell(0, 10, 'Error cargando la imagen: ' + str(e), 0, 1)

pdf.output('AETHER_Arquitectura.pdf', 'F')
print("Generado")
