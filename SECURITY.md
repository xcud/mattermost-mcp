# Security Policy

## Security Incident Log

### August 10, 2025 - Token Exposure Incident
- **Issue**: GitGuardian detected Mattermost token in documentation 
- **Action Taken**: Repository history cleaned, token references removed
- **Status**: Resolved - No active secrets in codebase
- **Recommendation**: Revoke exposed token and generate new one if needed

## Reporting Security Issues

If you discover a security vulnerability, please report it to:
- **Email**: ben@lit.ai
- **Priority**: High priority issues will be addressed within 24 hours

## Security Best Practices

- Never commit real tokens, passwords, or credentials
- Use environment variables for sensitive configuration
- Review commits before pushing to public repositories
- Use placeholder values in documentation and examples

