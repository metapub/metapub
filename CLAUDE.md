# CLAUDE.md

This file provides coding guidelines for Claude when working on the metapub project.

## Model Selection
1. **Never use Opus** - Always use Sonnet or Haiku models for this project.

## Import Guidelines
2. **Avoid in-function imports** - Place imports at the module level unless ABSOLUTELY necessary to avoid circular import problems. In-function imports should be a last resort and well-documented when used.

## Exception Handling
3. **Avoid huge try-except blocks** - Keep exception handling focused and specific to the operations that might fail.

4. **Don't catch generic exceptions** - Avoid `except Exception:` or bare `except:` blocks. Let programming errors (like AttributeError, TypeError, etc.) bubble up naturally. Only catch specific exceptions you can meaningfully handle.

5. **Let programming errors surface** - Don't suppress bugs by catching them generically. Better to fail fast and fix the underlying issue.

## Control Flow
6. **Avoid long if-else trees** - Use early returns, guard clauses, or dictionaries/switch patterns instead of deeply nested if-else chains. Prefer clear, linear code flow.

## Additional Guidelines
- Follow the existing code patterns and conventions in the metapub codebase
- Maintain the current architecture and design patterns
- Write clear, focused functions with single responsibilities