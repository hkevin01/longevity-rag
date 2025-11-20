# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **Do NOT** open a public issue
2. Email the maintainers with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. Allow reasonable time for a response (typically 48-72 hours)
4. We will work with you to understand and address the issue

## Security Best Practices

When using this project:

- Keep dependencies up to date
- Use environment variables for sensitive data (API keys, credentials)
- Never commit `.env` files
- Review code before deployment
- Use HTTPS for all external communications
- Validate and sanitize all inputs
- Follow principle of least privilege for permissions

## Known Security Considerations

- This project processes biomedical literature and data
- Ensure data privacy when using personal health information
- API keys should be stored securely in `.env` files
- Be mindful of rate limits when accessing external APIs

## Updates

Security updates will be released as patch versions and announced through:
- GitHub releases
- Project documentation
- Security advisories (for critical issues)
