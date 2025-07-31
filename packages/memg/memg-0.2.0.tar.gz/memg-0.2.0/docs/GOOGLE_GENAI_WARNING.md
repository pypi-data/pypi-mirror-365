# ⚠ GOOGLE GENAI PACKAGE WARNING ⚠

## CRITICAL: Do NOT Use `google-generativeai` - It's DEPRECATED!

### The Problem
There are **TWO** Google AI packages, and using the wrong one breaks everything:

1. **`google-genai`** - **CORRECT** (Modern, actively maintained)
2. **`google-generativeai`** - **WRONG** (Deprecated, legacy)

### The Linting Trap 🪤

**This is a common mistake that happens during "fixing" linting errors:**

1. Developer writes: `from google import genai` (correct)
2. Pylint complains: "import-error" or "no-name-in-module"
3. Developer thinks: "Let me fix this linting error"
4. Developer changes to: `import google.generativeai` (WRONG!)
5. Everything breaks because it's the deprecated package

### Why This Happens

- **Pylint doesn't recognize** the modern `google-genai` package
- **Old tutorials/docs** still reference `google-generativeai`
- **Auto-completion** might suggest the wrong package
- **"Fixing" linting errors** without understanding the packages

### The Solution 

**WE HAVE CONFIGURED THE PROJECT TO PREVENT THIS:**

1. **`.pylintrc`** - Disables import errors for `google-genai`
2. **`pyproject.toml`** - Configures all linting tools properly
3. **Code comments** - Clear warnings in the actual import lines
4. **This documentation** - Explains the issue completely

### Correct Usage Pattern

```python
# CORRECT - Modern google-genai package
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key=api_key)
```

### WRONG Pattern (Don't Do This!)

```python
# WRONG - Deprecated google-generativeai package
import google.generativeai as genai

# This is the OLD way - don't use it!
genai.configure(api_key=api_key)
```

### Dependencies

```toml
# CORRECT in requirements.txt/pyproject.toml
google-genai>=1.0.0

# WRONG - Don't use this!
google-generativeai>=0.8.5
```

### If Pylint Still Complains

If you see linting errors about `google-genai` imports:

1. **DO NOT change the import** - the package is correct
2. **Check `.pylintrc`** - Make sure it has our configuration
3. **Update pylint** - Older versions may not recognize the package
4. **Add to ignored imports** - If necessary, explicitly ignore the warning

### Package History

- **2024**: Google released new `google-genai` package (modern API)
- **2023**: `google-generativeai` was the main package (now legacy)
- **Current**: `google-genai` is the official, actively maintained package

### Verification Commands

```bash
# Check what's installed
pip list | grep google

# Should show: google-genai, NOT google-generativeai

# Test import works
python -c "from google import genai; print(' Modern google-genai works!')"
```

### Commit History

This issue was caused by commit `2c6bd34` which tried to "fix" pylint warnings by switching to the deprecated package. The fix was to revert to the working `google-genai` setup and configure linting properly.

---

**Remember: When in doubt, keep `google-genai` - it's the modern, correct package!** 
