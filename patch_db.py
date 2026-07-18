with open('app/src/main/java/com/example/db/AppDatabase.kt', 'r') as f:
    content = f.read()

content = content.replace(
    'entities = [Message::class, com.example.model.Reflexion::class]',
    'entities = [Message::class, com.example.model.Reflexion::class, com.example.model.EvolutionProposal::class]'
).replace(
    'version = 5',
    'version = 6'
).replace(
    'abstract fun reflexionDao(): ReflexionDao',
    'abstract fun reflexionDao(): ReflexionDao\n    abstract fun evolutionProposalDao(): EvolutionProposalDao'
)

with open('app/src/main/java/com/example/db/AppDatabase.kt', 'w') as f:
    f.write(content)
