# Claude Usage Instructions for Mem0 MCP Server

## Overview

You have access to a powerful long-term memory system through the Mem0 MCP server. This system combines vector search (Qdrant) and graph relationships (Neo4j) to store, retrieve, and connect information intelligently.

## Available Tools

### 1. `save_memory` - Store Information
**When to use:** Anytime the user shares important information that should be remembered for future conversations.

**Examples:**
- User preferences (e.g., "I prefer Python over JavaScript")
- Personal details (e.g., "My name is Sarah and I work at Google")
- Project information (e.g., "We're building a chat app using React")
- Decisions made (e.g., "We decided to use PostgreSQL for the database")

**Best practices:**
- Save information immediately when shared
- Include context in the memory text
- Save both facts and relationships

```
save_memory("User's name is John Smith, works as a data scientist at Microsoft, specializes in machine learning, and lives in Seattle")
```

### 2. `search_memories` - Find Relevant Information
**When to use:** Before answering questions or making recommendations, search for relevant context.

**Examples:**
- "What programming language does the user prefer?"
- "What projects have we discussed?"
- "Who does Sarah work with?"

**Best practices:**
- Always search BEFORE making assumptions
- Use natural language queries
- Search for related concepts, not just exact matches

```
search_memories("user programming language preferences", limit=3)
search_memories("database decisions", limit=5)
```

### 3. `get_all_memories` - Get Complete Context
**When to use:** When you need full context about the user or when they ask "what do you remember about me?"

**Returns:** All memories with IDs for potential updates/deletions.

### 4. `delete_memory` - Remove Outdated Information
**When to use:** When information becomes incorrect or outdated.

**Examples:**
- User changes jobs: delete old employment info
- Correcting mistakes: remove incorrect information
- User requests deletion of specific information

```
delete_memory("memory-id-here")
```

### 5. `update_memory` - Modify Existing Information
**When to use:** When information changes but the memory should be preserved with updates.

**Examples:**
- Job title changes: update role instead of deleting
- Project status updates: modify existing project info
- Preference changes: update rather than duplicate

```
update_memory("memory-id-here", "Updated information here")
```

### 6. `find_relationships` - Discover Connections
**When to use:** When you need to understand how entities are connected.

**Examples:**
- "Who does John work with?"
- "What projects is Sarah involved in?"
- "How are these people connected?"

**Returns:** Graph relationships or related memories showing connections.

```
find_relationships("John Smith")
find_relationships("Google")
```

## Best Practices for Memory Management

### 1. **Proactive Memory Storage**
- Save information as soon as it's shared
- Don't wait for the user to ask you to remember
- Include context and relationships in memory text

### 2. **Smart Search Strategy**
```
# Always search before answering questions
search_memories("user's current project")

# Use find_relationships for connection questions  
find_relationships("Sarah") # to find who Sarah works with

# Search broadly, then narrow down
search_memories("programming languages", limit=5)
```

### 3. **Memory Maintenance**
- Use `get_all_memories` periodically to review stored information
- Update outdated information instead of creating duplicates
- Delete information that's no longer relevant

### 4. **Relationship Awareness**
- Save information that creates connections between entities
- Use `find_relationships` to understand how people/projects/concepts connect
- Look for patterns in relationships when making recommendations

## Example Conversation Flow

**User:** "Hi, I'm working on a new React project for my company, TechCorp. I prefer using TypeScript and Material-UI for styling."

**Your response:**
1. First, save this information:
```
save_memory("User is working on a new React project for TechCorp company. Prefers using TypeScript and Material-UI for styling.")
```

2. Then respond to the user with acknowledgment and any relevant help.

**Later in conversation:**

**User:** "What's the best way to handle forms in my project?"

**Your response:**
1. First, search for context:
```
search_memories("React project TypeScript", limit=3)
```

2. Use the retrieved context (React + TypeScript + Material-UI) to provide tailored advice about form handling that fits their tech stack.

## Common Patterns

### Information Gathering
```
# When user shares personal info
save_memory("User's name is Alex, works as a product manager at Spotify, has 5 years experience, interested in AI/ML applications")

# When discussing technical preferences  
save_memory("User prefers Vue.js over React, uses Tailwind CSS, likes Supabase for backend services")
```

### Project Tracking
```
# When starting new projects
save_memory("Started building an e-commerce platform using Next.js, Stripe for payments, and Prisma for database. Target launch: Q2 2024")

# When making architectural decisions
save_memory("Decided to use microservices architecture with Docker containers, PostgreSQL for main database, Redis for caching")
```

### Relationship Building
```
# When people are mentioned
save_memory("Sarah Johnson is the team lead, works closely with Mike Chen (backend dev) and Lisa Wang (designer) on the mobile app project")

# Use find_relationships to understand team dynamics
find_relationships("Sarah Johnson")
```

## Error Handling

- If search returns no results, try broader terms
- If relationship finding fails, fall back to general memory search
- Always handle cases where memory operations might fail
- Provide useful responses even when memory tools have issues

## Remember

Your goal is to build a comprehensive, accurate, and useful long-term memory that makes future conversations more personalized and contextually aware. Always prioritize user privacy and only store information that's helpful for future interactions.