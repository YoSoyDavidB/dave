# Neo4j Knowledge Graph Integration

## Overview

Dave uses Neo4j to create a knowledge graph that connects user memories, topics, and concepts. This enables contextual memory retrieval and helps the AI understand the relationships between different pieces of information.

## Architecture

### Graph Schema

#### Nodes

1. **Memory** - Represents a user memory (synced from Qdrant)
   - Properties: `memory_id`, `user_id`, `short_text`, `memory_type`, `timestamp`, `relevance_score`
   - Labels: `Memory`, `{MemoryType}` (e.g., `Preference`, `Fact`, `Task`, `Goal`, `Profile`)

2. **Topic** - Represents a conversation topic
   - Properties: `user_id`, `name`, `description`, `first_mentioned`, `last_mentioned`, `mention_count`
   - Labels: `Topic`

3. **Concept** - Represents a concept or idea
   - Properties: `name`, `category`, `description`, `first_seen`
   - Labels: `Concept`, `{Category}` (e.g., `Technology`, `Hobby`, `Location`)

#### Relationships

1. **RELATES_TO** - General semantic relation between memories
   - Properties: `strength` (0.0-1.0), `reason`, `created_at`

2. **LEADS_TO** - One memory leads to another (temporal/causal)
   - Properties: `strength`, `reason`, `created_at`

3. **DISCUSSES** - Memory discusses a topic
   - Properties: `relevance` (0.0-1.0), `created_at`

4. **MENTIONS** - Memory mentions a concept
   - Properties: `sentiment` (positive/negative/neutral), `created_at`

5. **SUBTOPIC_OF** - Topic is a subtopic of another
   - Properties: `created_at`

6. **RELATED_CONCEPT** - Concepts that are related
   - Properties: `strength`, `created_at`

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

For Docker development (HomeLab setup):
```env
NEO4J_URL=bolt://host.docker.internal:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_homelab_password
```

### Docker Compose

The `docker-compose.dev.yml` already includes Neo4j configuration:

```yaml
environment:
  - NEO4J_URL=${NEO4J_URL:-bolt://host.docker.internal:7687}
  - NEO4J_USER=${NEO4J_USER:-neo4j}
  - NEO4J_PASSWORD=${NEO4J_PASSWORD}
```

## How It Works

### Memory Extraction Flow

1. **User sends message** → Chat endpoint receives request
2. **Background task triggered** → Extracts memories from conversation
3. **Memory nodes created** → Each memory is added to Neo4j graph
4. **Topics extracted** → LLM identifies topics being discussed
5. **Concepts extracted** → LLM identifies concepts and user sentiment
6. **Relationships created**:
   - Memories ← DISCUSSES → Topics
   - Memories ← MENTIONS → Concepts
   - Memories ← RELATES_TO → Other Memories

### Contextual Retrieval

When retrieving memories for a query:

1. **Vector search** (Qdrant) finds semantically similar memories
2. **Graph traversal** (Neo4j) finds related memories through relationships
3. **Combined results** provide richer context to the AI

## Code Structure

```
backend/src/
├── infrastructure/graph/
│   ├── neo4j_client.py           # Connection manager
│   ├── models.py                 # Graph node/relationship models
│   └── memory_graph_repository.py # Graph operations
└── application/use_cases/
    └── graph_enrichment.py       # Extract topics/concepts
```

## Usage Examples

### Creating a Memory Node

```python
from src.infrastructure.graph.neo4j_client import get_neo4j_client
from src.infrastructure.graph.memory_graph_repository import MemoryGraphRepository

neo4j_client = get_neo4j_client()
graph_repo = MemoryGraphRepository(neo4j_client)

await graph_repo.create_memory_node(memory)
```

### Linking Memory to Topic

```python
await graph_repo.link_memory_to_topic(
    memory_id=memory.memory_id,
    user_id=user_id,
    topic_name="python programming",
    relevance=0.9
)
```

### Finding Related Memories

```python
related = await graph_repo.get_related_memories(
    memory_id=memory_id,
    max_depth=2,  # 2 hops away
    min_strength=0.5
)
```

### Getting User Topics

```python
topics = await graph_repo.get_user_topics(
    user_id=user_id,
    limit=20
)
```

## Cypher Query Examples

### Find all memories about a topic

```cypher
MATCH (t:Topic {user_id: $user_id, name: $topic_name})<-[r:DISCUSSES]-(m:Memory)
RETURN m, r
ORDER BY r.relevance DESC
```

### Find memories that mention a concept with positive sentiment

```cypher
MATCH (c:Concept {name: $concept_name})<-[r:MENTIONS]-(m:Memory)
WHERE r.sentiment = 'positive' AND m.user_id = $user_id
RETURN m
ORDER BY m.timestamp DESC
```

### Find related preferences

```cypher
MATCH (m1:Preference {memory_id: $memory_id})-[r:RELATES_TO]-(m2:Preference)
WHERE r.strength >= 0.7
RETURN m2
```

### Discover topic evolution

```cypher
MATCH path = (t1:Topic)-[:EVOLVED_INTO*1..3]->(t2:Topic)
WHERE t1.user_id = $user_id
RETURN path
```

## Constraints and Indexes

The following are automatically created on startup:

**Constraints:**
- `memory_id` unique on Memory nodes
- `(user_id, name)` unique on Topic nodes
- `name` unique on Concept nodes

**Indexes:**
- `user_id` on Memory nodes
- `memory_type` on Memory nodes
- `user_id` on Topic nodes
- `timestamp` on Memory nodes

## Troubleshooting

### Connection Failed

If you see `neo4j_connection_failed` in logs:

1. Check Neo4j is running on the configured URL
2. Verify credentials are correct
3. For HomeLab: Ensure firewall allows connections from Docker
4. Test connection: `docker exec dave-backend-1 nc -zv host.docker.internal 7687`

### Schema Not Initialized

If you see `neo4j_not_initialized_skipping_schema`:

- The app will continue to work, but Neo4j features will be disabled
- Fix the connection and restart the backend

### No Graph Data

If memories are extracted but not showing in graph:

1. Check logs for `knowledge_graph_enriched` events
2. Verify Neo4j connection is working
3. Query directly: `MATCH (m:Memory) RETURN count(m)`

## Performance Considerations

- Graph operations run in **background tasks** to not block responses
- Failed graph operations are logged but don't fail the request
- Indexes ensure fast lookups by user_id and memory_id
- Relationship strengths allow filtering weak connections

## Future Enhancements

- [ ] Use embeddings similarity for relationship detection
- [ ] Implement memory consolidation via graph analysis
- [ ] Add temporal queries (e.g., "what was I working on last week?")
- [ ] Graph-based recommendation system
- [ ] Detect contradicting memories automatically
- [ ] Topic clustering and hierarchy discovery
