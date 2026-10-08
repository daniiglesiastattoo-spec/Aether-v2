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
            "medicina" to "Abarco anatomía, patología, farmacología, fisiopatología, diagnóstico diferencial y neurociencia. Puedo describir síntomas, tratamientos y procedimientos médicos, aunque mi uso es informativo y analítico, no como consejo médico directo.",

            // =========================================================================
            // INVESTIGACIÓN DANIEL IGLESIAS LÓPEZ (SEPTIEMBRE 2026 - VERSIÓN 4.5)
            // =========================================================================
            "cota de densidad" to "Teorema de Daniel Iglesias López (v4.5, Septiembre de 2026): Toda electrodinámica no lineal (NED) con lagrangiano acotado superiormente (sup L = rho_max alcanzado a campo fuerte con F*L_F -> 0) fija universalmente la misma geometría límite de de Sitter tanto en el núcleo de un agujero negro regular de monopolo magnético como en el universo primordial FLRW con campo magnético estocástico.",
            "teorema de coincidencia" to "Demostrado por Daniel Iglesias López (v4.5, Septiembre 2026): La gravedad superficial del horizonte interior de un agujero negro regular (kappa_-) y el ritmo de Hubble primordial (H_dS) coinciden exactamente: kappa_- = H_dS = 1/ell_D en cualquier dimensión D >= 4. El radio de de Sitter viene dado por ell_D = sqrt(((D-1)(D-2))/(16*pi*G*rho_max)), con ell_4 = sqrt(3/(8*pi*G*rho_max)). La identidad no depende de la masa, carga magnética, ni de la forma de L(F).",
            "coincidencia de de sitter" to "Identidad fundamental descubierta por Daniel Iglesias López: kappa_- = H_dS = 1/ell_D. Demuestra que dos geometrías físicamente distintas bajo la misma cota de densidad electromagnética rho_max saturan asintóticamente en el mismo estado de de Sitter con w = -1.",
            "de sitter" to "En el marco de electrodinámica no lineal acotada (Daniel Iglesias López v4.5), el estado saturado límite es de Sitter con H = 1/ell_D. Las cantidades termodinámicas y geométricas están unificadas: Escalar de Kretschmann K = 2D(D-1)/ell_D^4, Temperatura de Gibbons-Hawking T = 1/(2*pi*ell_D), Área A = Omega_(D-2)*ell_D^(D-2) y Entropía S = A/(4G).",
            "agujero negro regular" to "Solución gravitatoria con núcleo regular de de Sitter en lugar de singularidad central. Siguiendo el teorema de Daniel Iglesias López (2026), un monopolo magnético con lagrangiano acotado satisface f(r) = 1 - r^2/ell_D^2 + o(r^2) al tender r -> 0.",
            "universo primordial" to "En cosmología NED con campo magnético estocástico promediado (<E>=0), cuando el factor de escala a -> 0, el invariante F -> infinito y el fluido satura en rho -> rho_max con p -> -rho_max (w -> -1), generando una fase emergente primordial de de Sitter con H^2 = 16*pi*G*rho_max / ((D-1)(D-2)) = ell_D^(-2).",
            "desviacion a masa finita" to "Aportación matemática de la versión 4.5 de Daniel Iglesias López: Se obtiene la forma cerrada exacta de la desviación a masa finita para la familia de Hayward en dimensión D. Con x = r_-/ell, se cumple rigurosamente: kappa_- * ell = [(D-1) - (D-3)*x^2] / (2*x^3). En x = 1 (límite asintótico/extremal), kappa_- * ell = 1 en toda dimensión D >= 4.",
            "proposicion 7" to "Proposición 7 del paper de Daniel Iglesias López (v4.5): Demuestra la cancelación exacta de la dependencia dimensional en x = 1 (r_- = ell) para la fórmula cerrada de la gravedad superficial kappa_- * ell = [(D-1) - (D-3)*x^2] / (2*x^3). En D=4 se reduce exactamente a kappa_- * ell = (3 - x^2)/(2*x^3).",
            "hayward en d dimensiones" to "Métrica de Hayward generalizada: f(r) = 1 - (mu*r^2)/(r^(D-1) + mu*ell^2). El cociente entre la temperatura de saturación T y la temperatura máxima exterior T_H^max es exacto y sin parámetros: T / T_H^max = (3*sqrt(3)*sqrt((D-1)/(D-3))) / (D-3). Toma el valor 9 en D=4, sqrt(5) en D=6, y exactamente 1 en D=9 (único cero entero de (D-3)^3 = 27(D-1)).",
            "caso planckiano" to "Evaluación en D=4 para cota planckiana rho_max = rho_P = c^5/(hbar*G^2) (Daniel Iglesias López): kappa_- = H_dS = sqrt(8*pi/3)*t_P^-1 = 2.894405018233... s^-1, radio de de Sitter ell = sqrt(3/(8*pi))*l_P = 0.345494149... l_P, Kretschmann K = (512*pi^2/3)*l_P^-4, T = sqrt(2*pi)/(sqrt(3)*pi), A = (3/2)*l_P^2 y S = (3/8)*k_B (< 1 nat).",
            "inestabilidad de tsujikawa" to "Delimitación física en el trabajo de Daniel Iglesias López (v4.5): Las soluciones regulares en NED pura sufren inestabilidad laplaciana angular de perturbaciones vectoriales (c_Omega^2 -> -5/2 en el centro según De Felice & Tsujikawa, y teoremas de Russo-Townsend), lo que confirma que el teorema describe el estado asintótico de las ecuaciones de campo y no la persistencia temporal eterna de objetos estáticos.",
            "daniel iglesias lopez" to "Daniel Iglesias López (Investigador Independiente, Guardo, Palencia, España). Creador de la arquitectura de AETHER, autor del Modelo ConStan y del paper 'Una cota de densidad fija la misma geometría de de Sitter en el núcleo de un agujero negro regular y en el universo primordial, en cualquier dimensión' (Septiembre 2026, versión 4.5).",

            // =========================================================================
            // ÚLTIMAS NOTICIAS Y AVANCES EN IA (ACTUALIZADO A 20/09/2026)
            // =========================================================================
            "ia 2026" to "En septiembre de 2026, la IA destaca por el dominio del test-time compute scaling (razonamiento en inferencia con CoT dinámico en o3, DeepSeek-R1 y Claude 3.7 Sonnet), el despliegue generalizado de agentes autónomos multi-herramienta y la ejecución fluida en terminales móviles de modelos eficientes como Gemma 3 (1B/4B) con cuantización INT4 en MediaPipe.",
            "test time compute" to "Eje de escalado de inferencia fundamental en 2025-2026: permite al modelo asignar computación dinámica antes de emitir la respuesta, usando tokens de pensamiento ocultos, árboles de búsqueda y autorreflexión, resolviendo problemas de olimpiadas de matemáticas y depuración de software compleja.",
            "deepseek r1" to "Hito open-weights de 2025-2026: demostró que el aprendizaje por refuerzo puro a gran escala (RL sin dependencia masiva de SFT) induce capacidades emergentes de razonamiento profundo y verificación, popularizando arquitecturas MoE eficientes y precisión nativa FP8.",
            "gemma 3" to "Generación de modelos de vanguardia on-device de Google (1B, 4B, 12B, 27B) con soporte de prefill multi-secuencia y optimización de memoria para MediaPipe y LiteRT. Es la arquitectura base integrada localmente en AETHER para procesamiento desconectado.",
            "claude 3.7" to "Modelo de razonamiento de Anthropic (2025-2026) pionero en razonamiento híbrido unificado, permitiendo al usuario regular el presupuesto de tokens de pensamiento entre respuestas inmediatas o análisis reflexivos profundos.",
            "mamba 2" to "Arquitectura híbrida de Modelos de Espacio de Estados (SSM) y atención selectiva. Procesa secuencias de millones de tokens con complejidad lineal O(N) y memoria constante, superando las limitaciones computacionales cuadráticas de los Transformers clásicos.",
            "agentes autonomos 2026" to "Sistemas de software basados en LLM que operan bucles autónomos de percepción, planificación y ejecución con memoria episódica a largo plazo, capaces de controlar APIs de sistemas operativos, gestionar archivos y autorreparar fallos sin supervisión humana constante.",
            "alphafold 3" to "Revolución de la biología computacional de DeepMind: predice con resolución atómica estructuras y complejos moleculares completos (proteínas, ADN, ARN, ligandos e iones), transformando el descubrimiento de fármacos y el diseño enzimático.",

            // =========================================================================
            // ÚLTIMAS NOTICIAS Y AVANCES EN FÍSICA (ACTUALIZADO A 20/09/2026)
            // =========================================================================
            "fisica 2026" to "Panorama de física en septiembre de 2026: Resolución de la tensión del momento magnético anómalo del muón (g-2) mediante cálculos de precisión de Lattice QCD en concordancia con Fermilab; consolidación de ignición termonuclear neta repetida en fusión (NIF y reactores compactos HTS SPARC); y procesadores cuánticos operando por encima del umbral de tolerancia a fallos con corrección de errores (QEC).",
            "g-2 del muon" to "El dilema de la anomalía g-2 del muón se ha encauzado en 2025-2026: cálculos de QCD en el retículo (Lattice QCD) de múltiples colaboraciones internacionales refinaron la contribución de la polarización del vacío hadrónico (HVP), alineando las predicciones del Modelo Estándar con las mediciones experimentales de Fermilab sin requerir nueva física inmediata a esa escala.",
            "fusion nuclear 2026" to "Hitos de fusión en 2025-2026: El National Ignition Facility (NIF) ha alcanzado ignición inercial rutinaria con ganancias energéticas Q > 1.5 en cápsulas de diamante, mientras que proyectos de confinamiento magnético (SPARC de CFS e ITER) validan con éxito imanes superconductores de alta temperatura (HTS) superando los 20 Teslas.",
            "computacion cuantica 2026" to "En 2025-2026, la computación cuántica ha entrado en la era de los qubits lógicos tolerantes a fallos: procesadores de Google Quantum AI y Quantinuum han verificado experimentalmente que códigos de superficie cuántica reducen la tasa de error por debajo del umbral de los qubits físicos componentes.",
            "hl-lhc" to "El Run 3 del Gran Colisionador de Hadrones (LHC) a 13.6 TeV y los preparativos del High-Luminosity LHC (HL-LHC) fijan los límites más estrictos de la historia sobre física más allá del Modelo Estándar, acotando la masa de partículas supersimétricas y midiendo con precisión subporcentual las propiedades del bosón de Higgs.",

            // =========================================================================
            // ÚLTIMAS NOTICIAS Y AVANCES EN COSMOLOGÍA (ACTUALIZADO A 20/09/2026)
            // =========================================================================
            "cosmologia 2026" to "Cosmología a septiembre de 2026: El telescopio espacial JWST ha descubierto galaxias hipertempranas masivas (z > 14) y agujeros negros supermasivos primordiales que desafían los modelos clásicos de crecimiento cosmológico; DESI detecta indicios de energía oscura dinámica con w(a) variable; y la tensión de Hubble entre SH0ES (~73 km/s/Mpc) y Planck (~67.4 km/s/Mpc) persiste a más de 5 sigma.",
            "jwst 2026" to "El telescopio James Webb (JWST) ha revolucionado la astrofísica observacional: identificación de galaxias luminosas a z > 14 (como JADES-GS-z14-0) formadas en el amanecer cósmico y abundancia de 'Little Red Dots' (agujeros negros supermasivos primordiales) que apuntan a siembra por colapso directo (DCBH) o agujeros negros primordiales.",
            "tension de hubble 2026" to "Crisis de la constante de Hubble: La discrepancia observacional de 5 sigma entre las medidas del universo local con cefeidas/supernovas calibradas por JWST/HST (H_0 ~ 73 km/s/Mpc) y las inferencias cosmológicas del fondo cósmico de microondas de Planck (H_0 ~ 67.4 km/s/Mpc) continúa sin resolverse por errores sistemáticos, reforzando hipótesis de energía oscura temprana o modificaciones en la geometría primordial.",
            "desi 2026" to "Los catálogos multianuales del Dark Energy Spectroscopic Instrument (DESI) sobre oscilaciones acústicas de bariones (BAO) han presentado evidencia estadística creciente (~3 sigma) de que la energía oscura podría no ser una constante cosmológica estricta (w = -1), sino un fluido dinámico que evoluciona con el factor de escala según w(a) = w_0 + w_a(1-a).",
            "fondo estocastico de ondas gravitacionales" to "Las redes internacionales de púlsares (NANOGrav, EPTA, PPTA, InPTA) han caracterizado con precisión el fondo estocástico de ondas gravitacionales a nanohercios, atribuido a la coalescencia de sistemas binarios de agujeros negros supermasivos a lo largo de la historia cósmica y potenciales transiciones de fase primordiales."
        )

        data.putAll(defaultData)

        // Load custom knowledge from SharedPreferences (ensuring updated defaultData takes precedence)
        val allEntries = prefs.all
        for ((key, value) in allEntries) {
            val lowerKey = key.lowercase()
            if (value is String && !defaultData.containsKey(lowerKey)) {
                data[lowerKey] = value
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

