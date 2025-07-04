from mem0 import Memory
import os

# Custom instructions for memory processing
# These aren't being used right now but Mem0 does support adding custom prompting
# for handling memory retrieval and processing.
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Key Information: Identify and save the most important details.
- Context: Capture the surrounding context to understand the memory's relevance.
- Connections: Note any relationships to other topics or memories.
- Importance: Highlight why this information might be valuable in the future.
- Source: Record where this information came from when applicable.
"""

def get_mem0_client():
    # Get LLM provider and configuration
    llm_provider = os.getenv('LLM_PROVIDER')
    llm_api_key = os.getenv('LLM_API_KEY')
    llm_model = os.getenv('LLM_CHOICE')
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
    
    # Initialize config dictionary
    config = {}
    
    # Configure LLM based on provider
    if llm_provider == 'openai' or llm_provider == 'openrouter':
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000,
            }
        }
        
        # Set API key in environment if not already set
        if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = llm_api_key
            
        # Set custom base URL for OpenAI-compatible endpoints (like Google Gemini)
        llm_base_url = os.getenv('LLM_BASE_URL')
        if llm_base_url and not os.environ.get("OPENAI_BASE_URL"):
            os.environ["OPENAI_BASE_URL"] = llm_base_url
            
        # For OpenRouter, set the specific API key
        if llm_provider == 'openrouter' and llm_api_key:
            os.environ["OPENROUTER_API_KEY"] = llm_api_key
    
    elif llm_provider == 'ollama':
        config["llm"] = {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000,
            }
        }
        
        # Set base URL for Ollama if provided
        llm_base_url = os.getenv('LLM_BASE_URL')
        if llm_base_url:
            config["llm"]["config"]["ollama_base_url"] = llm_base_url
    
    # Configure embedder based on provider
    if llm_provider == 'openai':
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "model": embedding_model or "text-embedding-3-small",
                "embedding_dims": 1536  # Default for text-embedding-3-small
            }
        }
        
        # Set API key in environment if not already set
        if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = llm_api_key
    
    elif llm_provider == 'ollama':
        config["embedder"] = {
            "provider": "ollama",
            "config": {
                "model": embedding_model or "nomic-embed-text",
                "embedding_dims": 768  # Default for nomic-embed-text
            }
        }
        
        # Set base URL for Ollama if provided
        embedding_base_url = os.getenv('LLM_BASE_URL')
        if embedding_base_url:
            config["embedder"]["config"]["ollama_base_url"] = embedding_base_url
    
    # Configure vector store based on provider
    vector_store_provider = os.getenv('VECTOR_STORE_PROVIDER', 'supabase')
    
    if vector_store_provider == 'qdrant':
        qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        # Determine embedding dimensions based on the actual embedding model
        embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE', '')
        if 'embedding-001' in embedding_model:  # Google Gemini embedding model
            embedding_dims = 768
        elif llm_provider == "openai":
            embedding_dims = 1536
        else:
            embedding_dims = 768  # Default for other providers
            
        qdrant_config = {
            "collection_name": os.getenv('QDRANT_COLLECTION', 'mem0_memories'),
            "embedding_model_dims": embedding_dims
        }
        
        # For cloud instances (URLs starting with https://), don't specify port
        if qdrant_host.startswith('https://'):
            qdrant_config["url"] = qdrant_host
        else:
            # For local instances, use host and port
            qdrant_config["host"] = qdrant_host
            qdrant_config["port"] = int(os.getenv('QDRANT_PORT', '6333'))
        
        config["vector_store"] = {
            "provider": "qdrant",
            "config": qdrant_config
        }
        
        # Add API key if provided (for Qdrant Cloud)
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        if qdrant_api_key:
            config["vector_store"]["config"]["api_key"] = qdrant_api_key
    else:
        # Determine embedding dimensions based on the actual embedding model
        embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE', '')
        if 'embedding-001' in embedding_model:  # Google Gemini embedding model
            embedding_dims = 768
        elif llm_provider == "openai":
            embedding_dims = 1536
        else:
            embedding_dims = 768  # Default for other providers
            
        # Default to Supabase for backward compatibility
        config["vector_store"] = {
            "provider": "supabase",
            "config": {
                "connection_string": os.environ.get('DATABASE_URL', ''),
                "collection_name": "mem0_memories",
                "embedding_model_dims": embedding_dims
            }
        }
    
    # Add standardized graph extraction schema to reduce entity type inconsistencies
    standardized_graph_prompt = """
Extract entities and relationships using ONLY these standardized types to ensure consistency:

ENTITY TYPES (use exactly these labels):
- person: Individual people (use full names when available)
- organization: Companies, institutions, groups, teams
- location: Cities, countries, addresses, places  
- skill: Technical or professional abilities
- role: Job titles or positions
- technology: Programming languages, tools, frameworks
- project: Work projects, initiatives, products
- hobby: Personal interests and activities

RELATIONSHIP TYPES (use exactly these):
- works_at: person -> organization
- lives_in: person -> location
- has_skill: person -> skill  
- has_role: person -> role
- uses_technology: person -> technology
- works_on: person -> project
- enjoys: person -> hobby
- collaborates_with: person -> person
- married_to: person -> person
- reports_to: person -> person
- manages: person -> person
- member_of: person -> organization

STRICT RULES:
1. Use ONLY the entity and relationship types listed above
2. Convert names to lowercase with underscores (e.g., "John Smith" -> "john_smith")
3. If unsure about type, use the closest standard type from the list
4. Do NOT create new entity or relationship types
5. Prefer "person" over "people", "individual", "user", etc.
6. Prefer "organization" over "company", "business", "firm", etc.

Example:
Input: "Sarah Chen is a data scientist at Google who specializes in NLP and lives in Mountain View"
Output: [
  {"source": "sarah_chen", "source_type": "person", "relationship": "works_at", "target": "google", "target_type": "organization"},
  {"source": "sarah_chen", "source_type": "person", "relationship": "has_role", "target": "data_scientist", "target_type": "role"},
  {"source": "sarah_chen", "source_type": "person", "relationship": "has_skill", "target": "nlp", "target_type": "skill"},
  {"source": "sarah_chen", "source_type": "person", "relationship": "lives_in", "target": "mountain_view", "target_type": "location"}
]
"""

    # Configure Neo4j graph store if credentials are provided
    neo4j_url = os.getenv('NEO4J_URL')
    neo4j_username = os.getenv('NEO4J_USERNAME')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    
    if neo4j_url and neo4j_username and neo4j_password:
        config["graph_store"] = {
            "provider": "neo4j",
            "config": {
                "url": neo4j_url,
                "username": neo4j_username,
                "password": neo4j_password
            }
            # Temporarily removing custom_prompt to test basic functionality
            # "custom_prompt": standardized_graph_prompt
        }

    # config["custom_fact_extraction_prompt"] = CUSTOM_INSTRUCTIONS
    
    # Create and return the Memory client
    return Memory.from_config(config)