# MEMG Contributors Memory System - Docker Quick Start

## **Official Docker Deployment**

### **Step 1: Pull Official Container**
```bash
docker pull ghcr.io/genovo-ai/memg:dev
```

### **Step 2: Setup Environment**
```bash
# Copy example environment file
cp example.env .env

# Edit with your Google API key
nano .env
# Update line 106: GOOGLE_API_KEY=your_actual_api_key_here
```

### **Step 3: Run Container**
```bash
# Basic run (ephemeral storage)
docker run --rm --env-file .env -p 8787:8787 ghcr.io/genovo-ai/memg:dev

# Production run (persistent storage)
mkdir -p data/{kuzu,qdrant}
docker run -d --name memg-server \
 --env-file .env \
 -v ./data/kuzu:/app/internal_storage/kuzu \
 -v ./data/qdrant:/app/internal_storage/qdrant \
 -p 8787:8787 \
 --restart unless-stopped \
 ghcr.io/genovo-ai/memg:dev
```

### **Step 4: Verify Deployment**
```bash
# Health check
curl http://localhost:8787/health

# Expected response:
# {"status":"healthy","service":"g^mem v0.2 MCP Server","version":"v0.2","memory_system_initialized":true}
```

## **Configuration**

### **Required Settings:**
- `GOOGLE_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### **Optional Tuning:**
- `MEMG_SIMILARITY_THRESHOLD=0.7` - Memory similarity (0.0-1.0)
- `MEMORY_SYSTEM_LOG_LEVEL=INFO` - Logging level
- `MEMG_MESSAGE_WINDOW_SIZE=10` - Context window size

## **MEMG Contributors Network Integration**

### **MCP Connection:**
- **Port:** 8787
- **Protocol:** Server-Sent Events (SSE)
- **Health Endpoint:** `/health`

### **Network Topology:**
```
 M2 Mac (Dev) → Docker Container (MCP Hub) ← 📱 M3 Mac (Prod)
```

## 🛡 **Security Notes**

- No hardcoded secrets in container
- Runtime environment configuration
- Secure API key management
- Production-ready deployment

---

**Ready for MEMG Contributors autonomous deployment! **
