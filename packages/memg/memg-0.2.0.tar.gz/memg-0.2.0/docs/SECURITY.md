# Security Guidelines for MEMG Contributors Memory System

## 🚨 Critical Security Practices

### 1. API Key Management

**NEVER commit API keys to version control!**

#### Correct Approach:
```bash
# Use environment variables
export GOOGLE_API_KEY="your_actual_api_key_here"
docker run -e GOOGLE_API_KEY="$GOOGLE_API_KEY" ghcr.io/genovo-ai/memg:latest
```

#### WRONG - Never Do This:
```dockerfile
# DON'T hardcode API keys in Dockerfiles!
ENV GOOGLE_API_KEY=AIzaSyC98M6kXnCmV78LFPF6c2ppJNvyFg8-dUY
```

### 2. Environment Configuration

1. **Copy the template:**
 ```bash
 cp .env.example .env
 ```

2. **Edit with your real values:**
 ```bash
 # Edit .env file with your actual API keys
 nano .env
 ```

3. **Verify .env is in .gitignore:**
 ```bash
 grep "\.env" .gitignore
 ```

### 3. Docker Security

#### Development:
```bash
# Load from .env file
docker run --env-file .env ghcr.io/genovo-ai/memg:dev
```

#### Production:
```bash
# Use secrets management
docker run -e GOOGLE_API_KEY="$(cat /run/secrets/google_api_key)" \
 ghcr.io/genovo-ai/memg:latest
```

### 4. CI/CD Security

- API keys are **NOT** included in Docker images
- Use GitHub Secrets for production deployments
- Environment-specific configurations are handled at runtime

### 5. API Key Rotation

1. Generate new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update environment variables
3. Restart services
4. Revoke old API key

## 🛡 Security Checklist

- [ ] No hardcoded API keys in code
- [ ] `.env` file is in `.gitignore`
- [ ] Production uses secrets management
- [ ] Regular API key rotation
- [ ] Monitoring for exposed keys in logs
- [ ] Least privilege access principles

## 🚨 If API Key is Compromised

1. **Immediately revoke** the compromised key
2. **Generate new** API key
3. **Update all environments**
4. **Review access logs** for unauthorized usage
5. **Rotate any related secrets**

## 📞 Security Contact

For security issues, contact: security@genovo-ai.com
