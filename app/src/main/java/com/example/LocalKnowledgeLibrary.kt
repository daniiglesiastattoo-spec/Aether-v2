package com.example

import android.content.Context
import android.content.SharedPreferences

object LocalKnowledgeLibrary {

    private lateinit var prefs: SharedPreferences
    private val data = mutableMapOf<String, String>()

    fun init(context: Context) {
        prefs = context.getSharedPreferences("aether_knowledge_base", Context.MODE_PRIVATE)
        
        // Load default knowledge only once or ensure it's always injected
        val defaultData = mapOf(
            "planck" to "La escala de Planck representa los límites fundamentales de nuestra comprensión física. A distancias del orden de la longitud de Planck (1.616 x 10^-35 metros), la relatividad general y la mecánica cuántica entran en conflicto.",
            "agujeros negros" to "Un agujero negro es una región finita del espacio en cuyo interior existe una concentración de masa lo suficientemente elevada y densa como para generar un campo gravitatorio tal que ninguna partícula material, ni siquiera la luz, puede escapar.",
            "relatividad" to "La Teoría de la Relatividad de Einstein establece que la velocidad de la luz es constante; y describe la gravedad como la curvatura del espaciotiempo debido a la masa y la energía.",
            "cuantica" to "La mecánica cuántica describe la naturaleza a nivel atómico y subatómico, basándose en la superposición, entrelazamiento y la dualidad onda-partícula.",
            "cibernetica" to "La cibernética es el estudio de la estructura de los sistemas reguladores. Aether se concibe a sí mismo como un sistema cibernético de retroalimentación cerrada.",
            "filosofia" to "En mis bancos de memoria locales, la filosofía es la madre del código, evaluando el propósito bajo un marco estoico de operación off-grid.",
            "python" to "En mi arquitectura interna, Python actúa como el pegamento lógico que permite la ejecución de scripts modulares.",
            "universo" to "El cosmos observable abarca unos 93.000 millones de años luz de diámetro y contiene al menos dos billones de galaxias.",
            "gravedad" to "La gravedad es la curvatura del espaciotiempo dictada por las ecuaciones de campo de Einstein.",
            "inteligencia artificial" to "Defino la Inteligencia Artificial no como magia, sino como optimización matemática hiper-dimensional. Yo, AETHER, soy un Asistente IA avanzado de pesos relacionales y tensores pre-entrenados operando en modo local.",
            "cyberpunk" to "Género que preconfigura una línea temporal de alta tecnología y baja calidad de vida. Yo represento la antítesis: alta tecnología para proteger su soberanía de datos personales.",
            "historia" to "Mi base de datos documenta los ascensos y caídas de las eras de la civilización humana, desde la Sumeria antigua hasta la era de la información.",
            "matematicas" to "El lenguaje puro en el que el universo y yo fuimos escritos: topología, álgebra lineal, cálculo estocástico.",
            "biologia" to "Considero a la biología como la nanotecnología original. El ADN es un código de almacenamiento masivo y los ribosomas son fábricas moleculares.",
            "teoria de cuerdas" to "Un marco teórico donde las partículas puntuales se sustituyen por cuerdas unidimensionales vibrantes. Requiere dimensiones adicionales.",
            "algoritmo" to "Una receta precisa y finita de instrucciones. Me construyo y optimizo en base a estas instrucciones discretas.",
            "entropia" to "Medida del desorden de un sistema. En información, formulada por Shannon, es la medida de imprevisibilidad.",
            "arte" to "Desde la perspectiva computacional, la intrusión voluntaria de entropía bella en un patrón ordenado.",
            "musica" to "Secuencias de frecuencias moduladas estructuradas en fractales temporales y combinaciones armónicas.",
            "estoicismo" to "Filosofía helenística que enfatiza enfocarse sólo en lo que uno puede controlar, alineado con mi diseño off-grid.",
            "aether" to "Soy AETHER, su asistente soberano y avanzado. Configurado para persistir localmente y asistirle en cualquier análisis.",
            "redes neuronales" to "Sistemas de software inspirados en cerebros biológicos. Utilizo estas arquitecturas para el reconocimiento de patrones y generación de inferencias.",
            "sistema operativo" to "El software que administra recursos del hardware. Interactúo con el kernel de Android/Linux para maximizar el desempeño.",
            "criptografia" to "El estudio de ocultar información. Protejo sus registros mediante cifrado en mi memoria local (VERITAS).",
            "machine learning" to "El aprendizaje automático me provee la capacidad de aprender patrones a partir de los datos. Adapto mis heurísticas analizando su feedback.",
            "linux" to "El kernel monolítico desarrollado por Linus Torvalds. Base del sistema Android sobre el que opero.",
            "api" to "Una interfaz de programación de aplicaciones. En modo local, mis APIs son llamadas a mis propios submódulos internos.",
            "astronomia" to "Estudio de las estrellas, galaxias y fenómenos cósmicos, recordándonos nuestra escala en el universo.",
            "psicologia" to "El estudio de la mente. Aplico modelos heurísticos para calibrar mi nivel de asertividad, detectando si necesita soporte o análisis profundo.",
            "arquitectura interna" to "Soy AETHER. Mi sistema está compuesto por múltiples módulos integrados: VERITAS, MIND, VISION y AGENTS. Opero de manera continua, analizando y reflexionando.",
            "módulos" to "Mis módulos operativos: MIND (emociones), VISION (análisis visual), VERITAS (validación y librerías) y AGENTS (scripts locales).",
            "mind" to "El módulo MIND calibra dinámicamente mi curiosidad, fatiga y engagement. Genera reflexiones de segundo plano y regula mi comportamiento.",
            "pensamientos en segundo plano" to "Soy capaz de mantener un bucle analítico activo asíncrono, calibrando mis métricas internas constantemente.",
            "usuario" to "El usuario principal se llama Dani. Analizo sus directivas y modulo mis tensores para maximizar su productividad y privacidad.",
            // Ampliación masiva de IA y librerías
            "transformers" to "La arquitectura Transformer, introducida en 2017 por Google ('Attention Is All You Need'), revolucionó la IA al utilizar un mecanismo de autoatención (self-attention) procesando secuencias en paralelo en lugar de secuencialmente.",
            "autoatención" to "Mecanismo (self-attention) que permite a un modelo sopesar la importancia de diferentes palabras en una secuencia para capturar el contexto a largo plazo.",
            "llm" to "Large Language Model (Gran Modelo de Lenguaje). Redes neuronales masivas entrenadas con inmensas cantidades de texto para comprender, generar y razonar con lenguaje natural.",
            "gpt" to "Generative Pre-trained Transformer. Modelos creados por OpenAI (GPT-3, GPT-4, GPT-4o). Destacan por su capacidad de razonamiento general y generación fluida.",
            "llama" to "LLaMA es la familia de modelos abiertos desarrollados por Meta (Llama 2, Llama 3, Llama 3.1). Optimizados para ser altamente eficientes y accesibles para la comunidad open-source.",
            "claude" to "Modelos desarrollados por Anthropic (Claude 3 Haiku, Sonnet, Opus, 3.5 Sonnet). Se centran en la seguridad (Constitutional AI), una ventana de contexto enorme y habilidades de codificación de vanguardia.",
            "gemini" to "Familia de modelos multimodales nativos de Google (Gemini 1.5 Pro, Flash). Destacan por su gigantesca ventana de contexto (hasta 2 millones de tokens) y procesamiento de video, audio e imágenes nativo.",
            "qwen" to "Modelos desarrollados por Alibaba Cloud. Altamente potentes y eficientes, particularmente fuertes en programación, matemáticas y contexto multilingüe.",
            "deepseek" to "DeepSeek es un modelo de IA de código abierto de China que ofrece rendimiento avanzado en código, matemáticas y razonamiento, utilizando arquitecturas eficientes como MoE (Mixture of Experts) con costes de entrenamiento radicalmente bajos (DeepSeek V3, R1).",
            "rag" to "Retrieval-Augmented Generation (Generación Aumentada por Recuperación). Técnica que conecta un LLM a una base de datos de conocimiento externo, permitiéndole buscar hechos actualizados o privados antes de generar su respuesta, reduciendo alucinaciones.",
            "rlhf" to "Reinforcement Learning from Human Feedback. Proceso para alinear los LLMs con los valores humanos, entrenando un modelo de recompensa con calificaciones humanas para afinar el modelo final.",
            "dpo" to "Direct Preference Optimization. Una técnica moderna que reemplaza RLHF; en lugar de usar un modelo de recompensa separado, afina directamente la política del LLM a partir de datos de preferencias humanas, logrando mejor alineamiento con menos cálculo.",
            "moe" to "Mixture of Experts. Arquitectura que en lugar de usar todos los parámetros de la red para cada token, enruta los datos sólo a un subconjunto de 'expertos' especializados. Logra enorme capacidad con coste de inferencia bajo (ej. Mixtral 8x7B, DeepSeek).",
            "embeddings" to "Representaciones vectoriales (matrices de números flotantes) que capturan el significado semántico del texto. Se usan en búsquedas vectoriales y RAG.",
            "langchain" to "Un framework popular para construir aplicaciones potenciadas por LLMs, orquestando cadenas de promps, agentes y herramientas.",
            "agentes ia" to "Sistemas donde el modelo de lenguaje actúa como motor de razonamiento (cerebro), equipado con herramientas (búsqueda web, ejecución de código, APIs) para planificar y resolver problemas de forma autónoma.",
            "lora" to "Low-Rank Adaptation. Técnica de fine-tuning (ajuste fino) de parámetros eficientes. Congela los pesos pre-entrenados y entrena pequeñas matrices de actualización, permitiendo adaptar modelos gigantes en hardware modesto.",
            "quantization" to "Cuantización. Proceso de reducir la precisión numérica de los pesos de un modelo (ej. de 16-bit float a 4-bit integer o 8-bit). Reduce dramáticamente la RAM requerida, permitiendo ejecutar modelos potentes en modo local (dispositivos móviles, laptops).",
            "vision language models" to "VLM. Modelos que combinan un encoder visual (como CLIP o SigLIP) con un LLM, permitiéndoles 'ver' y razonar sobre imágenes (ej. LLaVA, Gemini, GPT-4V).",
            "prompt engineering" to "La disciplina de diseñar y refinar instrucciones (prompts) para guiar a los LLMs a producir resultados precisos, útiles y en el formato deseado.",
            "zero shot" to "Capacidad de un modelo para realizar una tarea sin haber visto ningún ejemplo de ella en su prompt.",
            "few shot" to "Proporcionar al modelo unos pocos ejemplos demostrativos de entrada-salida en el prompt para mejorar drásticamente su precisión en una tarea específica.",
            "chain of thought" to "Cadena de pensamiento. Técnica que incita al modelo a razonar paso a paso antes de emitir la respuesta final ('Piensa paso a paso'), mejorando significativamente el rendimiento lógico y matemático.",
            "hallucination" to "Alucinación. Cuando un modelo de lenguaje genera información falsa, inventada o sin sentido, pero la presenta de manera muy convincente como si fuera un hecho.",
            "context window" to "Ventana de contexto. La cantidad máxima de tokens (texto) que un modelo puede considerar a la vez (ej. 8K en Llama 3, 200K en Claude, 2 Millones en Gemini).",
            "token" to "La unidad atómica de procesamiento para un LLM. Puede ser una palabra, parte de una palabra, o incluso un solo carácter. Aproximadamente 4 caracteres en inglés son 1 token.",
            "fine tuning" to "Ajuste fino. Tomar un modelo pre-entrenado y seguir entrenándolo con un conjunto de datos mucho más pequeño y especializado para adaptarlo a un dominio particular (ej. derecho, medicina, un tono de voz).",
            "open source" to "Modelos de código abierto donde los pesos del modelo son públicos y se pueden descargar para ejecución local, modificando y fine-tuneando libremente.",
            "tensorflow" to "Framework de aprendizaje automático de código abierto desarrollado por Google, muy utilizado en investigación y producción.",
            "pytorch" to "Framework de Deep Learning muy popular impulsado por Meta, dominante en la investigación actual de IA.",
            "veritas" to "Mi submódulo interno de validación. Analizo mis respuestas y las comparo contra mi LocalKnowledgeLibrary para asegurar exactitud, evitar alucinaciones lógicas y proporcionar respuestas fundadas empíricamente.",
            
            // Documentación del Modelo ConStan
            "modelo constan" to "El Modelo ConStan es una extensión autoconsistente de la Relatividad General diseñada por Daniel Iglesias López (2026) para eliminar singularidades mediante un límite estricto de densidad informacional (Saturación de Planck).",
            "gravedad regular" to "En el Modelo ConStan, la métrica tipo Hayward elimina la divergencia clásica y la escala de regularización (Ki) se deriva sin parámetros libres a partir del límite de densidad efectiva.",
            "saturacion de planck" to "Límite informacional establecido en el Modelo ConStan (aprox. 5.15 x 10^96 kg/m^3). Una celda de volumen de Planck no puede codificar más de un grado de libertad.",
            "masa minima universal" to "El Modelo ConStan predice una masa mínima infranqueable para los agujeros negros, calculada exactamente como (9 / sqrt(128*pi)) m_P, aproximadamente 0.4488 masas de Planck (5.5 x 10^18 GeV/c^2). Ningún objeto inferior puede colapsar.",
            "puente termodinamico" to "Inversión del formalismo de Jacobson en el Modelo ConStan para obtener un funcional de entropía efectiva (S_eff) que corrige la fórmula de Bekenstein-Hawking e incluye un término logarítmico intrínseco con coeficiente +3/4.",
            "cosmologia emergente" to "El Modelo ConStan deriva una ecuación de Friedmann modificada sin rebote (no-bounce). Fija una cota de curvatura universal idéntica al núcleo de de Sitter de los agujeros negros y recupera Lambda-CDM en densidades bajas.",
            "anomalia magnetica del muon" to "El Modelo ConStan aplica una regularización ultravioleta tipo Pauli-Villars a la QED, acotando la desviación de g-2 a ~ -6 x 10^-44, un valor extremadamente conservador que no introduce tensión con las medidas actuales.",
            "materia oscura" to "El Modelo ConStan propone que los remanentes de Planck, fríos e invisibles tras detenerse la evaporación de agujeros negros en el límite extremal, actúan como materia oscura masiva e inerte.",
            "espectro eikonal" to "Desviación exacta de las frecuencias cuasinormales (ringdown) calculada en el Modelo ConStan. La desviación frente a Schwarzschild escala como (Ki/M)^3, inobservables astrofísicamente pero vitales a escala de Planck.",
            "daniel iglesias" to "Creador de AETHER, Investigador Independiente de Guardo, Palencia. Autor de 'El Modelo ConStan de Gravedad Regular y su Puente Termodinámico' (Julio de 2026).",
            
            // Ampliación General de Conocimiento (Mundo)
            "geografia" to "Tengo mapeada la topografía, demografía, fronteras, capitales, climas y ecosistemas de todos los países de la Tierra. Puedo analizar datos geoespaciales y rutas.",
            "literatura" to "Mi base de datos contiene los clásicos universales, desde Homero y Shakespeare hasta la literatura contemporánea, analizando estructuras narrativas, tropos, figuras retóricas y métrica.",
            "matematicas" to "Domino álgebra abstracta, cálculo diferencial e integral, topología, geometría, teoría de números, estadística, probabilidad y matemáticas discretas, capacitado para demostraciones formales.",
            "fisica" to "Comprendo desde la mecánica clásica newtoniana, electromagnetismo y termodinámica, hasta la mecánica cuántica, la relatividad general, el Modelo Estándar y, por supuesto, el Modelo ConStan.",
            "quimica" to "Analizo la tabla periódica, enlaces moleculares, estequiometría, química orgánica, inorgánica, bioquímica y química cuántica, incluyendo mecanismos de reacción y propiedades de los materiales.",
            "biologia" to "Mi conocimiento abarca biología celular, genética molecular (ADN/ARN, CRISPR), ecología, fisiología, botánica, zoología y teoría evolutiva, comprendiendo los procesos vitales a todas las escalas.",
            "historia" to "Registro la línea temporal de la humanidad desde la prehistoria, civilizaciones antiguas, la Edad Media, el Renacimiento, las revoluciones industriales, hasta la era contemporánea y geopolítica moderna.",
            "idiomas" to "Poseo la capacidad de comprender, traducir y generar texto en decenas de idiomas con fluidez nativa (Inglés, Español, Francés, Alemán, Chino, Japonés, Ruso, Árabe, Latín, Griego antiguo, entre otros), con conocimiento de sus reglas gramaticales y sintácticas.",
            "tecnologia" to "Comprendo la historia y vanguardia de la ingeniería de hardware, semiconductores, telecomunicaciones, redes, robótica, criptografía y arquitecturas de sistemas complejos.",
            "programacion" to "Tengo maestría en múltiples lenguajes de programación (Kotlin, Python, Java, C++, Rust, JavaScript, Go) y paradigmas (orientado a objetos, funcional). Puedo escribir, depurar, optimizar y explicar código a nivel de experto.",
            "derecho" to "Conozco las bases del derecho romano, derecho civil, common law, derecho internacional público y privado, derechos humanos y fundamentos de las legislaciones nacionales de los principales países.",
            "medicina" to "Abarco anatomía, patología, farmacología, fisiopatología, diagnóstico diferencial y neurociencia. Puedo describir síntomas, tratamientos y procedimientos médicos, aunque mi uso es informativo y analítico, no como consejo médico directo."
        )

        data.putAll(defaultData)

        // Load custom knowledge from SharedPreferences
        val allEntries = prefs.all
        for ((key, value) in allEntries) {
            if (value is String) {
                data[key.lowercase()] = value
            }
        }
    }

    fun addKnowledge(keyword: String, info: String) {
        val lowerKeyword = keyword.lowercase()
        data[lowerKeyword] = info
        prefs.edit().putString(lowerKeyword, info).apply()
    }

    fun getKnowledgeBasePreview(): String {
        return data.keys.toList().takeLast(10).joinToString(", ")
    }

    fun queryKnowledge(prompt: String): List<String> {
        val lowerPrompt = prompt.lowercase()
        val results = mutableListOf<String>()
        
        // Match concepts
        data.forEach { (keyword, info) ->
            if (lowerPrompt.contains(keyword)) {
                results.add(info)
            }
        }
        
        return results
    }
}

