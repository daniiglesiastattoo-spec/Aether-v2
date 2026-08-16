from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []

    title_style = styles['Heading1']
    h2_style = styles['Heading2']
    h3_style = styles['Heading3']
    body_style = styles['BodyText']

    Story.append(Paragraph("AETHER - Architectural Schematic and Breakdown", title_style))
    Story.append(Spacer(1, 0.2 * inch))

    Story.append(Paragraph("1. Core Engine (AETHER CORE)", h2_style))
    Story.append(Paragraph("The central orchestration system of AETHER. It runs as a persistent background service (AetherCoreService) and maintains the agent's state, priorities, and physical awareness (battery, memory, network). It uses a 'heartbeat' (latido) mechanism to continuously monitor its environment and internal activation levels.", body_style))
    Story.append(Spacer(1, 0.1 * inch))

    Story.append(Paragraph("2. Mind & Cognitive Processing (MIND)", h2_style))
    Story.append(Paragraph("This module handles reasoning and decision making. It integrates multiple inference engines:", body_style))
    Story.append(Paragraph("- LocalLlmEngine: For on-device, private, and offline processing.", body_style))
    Story.append(Paragraph("- GeminiService & GroqService: Cloud-based inference for complex reasoning and high-speed execution.", body_style))
    Story.append(Spacer(1, 0.1 * inch))

    Story.append(Paragraph("3. Vision and Perception (VISION)", h2_style))
    Story.append(Paragraph("The visual perception system, managed by VisionManager and LocalVisionEngine. It allows AETHER to perceive and analyze its surroundings using the device's camera.", body_style))
    Story.append(Spacer(1, 0.1 * inch))

    Story.append(Paragraph("4. Memory and Self-Reflection (EVOLUTION)", h2_style))
    Story.append(Paragraph("A highly advanced self-improving module consisting of:", body_style))
    Story.append(Paragraph("- ReflexionEngine: Analyzes recent conversations and generates insights to improve future interactions.", body_style))
    Story.append(Paragraph("- EvolutionScanner: Continuously scans for evolution proposals in parameters, memory, architecture, code, and performance, gathering evidence to self-optimize.", body_style))
    Story.append(Spacer(1, 0.1 * inch))

    Story.append(Paragraph("5. Knowledge Base (VERITAS)", h2_style))
    Story.append(Paragraph("Managed by LocalKnowledgeLibrary and AppDatabase, this serves as AETHER's local, verified, and persistent memory of facts, user preferences, and internal state history.", body_style))
    Story.append(Spacer(1, 0.1 * inch))
    
    Story.append(Paragraph("6. Execution and Agents (AGENTS)", h2_style))
    Story.append(Paragraph("Interfaces with the external world and executes tools. Includes VoiceManager for auditory interaction and PythonBridgeManager for executing code or interfacing with external scripts.", body_style))
    Story.append(Spacer(1, 0.2 * inch))

    # Add the schematic image generated earlier
    try:
        # Assuming the image from earlier is available, wait, we don't know its exact name easily, we can find it.
        import glob
        img_path = glob.glob('/app/src/main/res/drawable/aether_schematic_*.jpg')[0]
        im = Image(img_path, width=6*inch, height=6*inch)
        Story.append(im)
    except Exception as e:
        Story.append(Paragraph(f"[Schematic Image not found: {str(e)}]", body_style))

    doc.build(Story)

create_pdf("AETHER_Architecture.pdf")
print("PDF generated successfully.")
