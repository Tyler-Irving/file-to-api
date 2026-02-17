# Contributing to File-to-API

Thank you for your interest in contributing to File-to-API! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We aim to foster a welcoming community for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, Node version, browser)
- **Screenshots or logs** if applicable

### Suggesting Features

Feature requests are welcome! Please include:
- **Use case** — Why is this feature needed?
- **Proposed solution** — How would it work?
- **Alternatives considered** — What other approaches did you think about?

### Pull Requests

1. **Fork the repository** and create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Test your changes** thoroughly:
   ```bash
   # Backend tests
   cd backend
   python manage.py test

   # Frontend (if applicable)
   cd frontend
   npm run build  # Ensure no TypeScript errors
   ```

4. **Commit with clear messages:**
   ```bash
   git commit -m "Add: Feature description"
   # Use prefixes: Add, Fix, Update, Remove, Refactor, Docs
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** with:
   - Description of changes
   - Related issue number (if applicable)
   - Screenshots for UI changes
   - Testing notes

## Development Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Code Style Guidelines

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for classes and functions
- Keep functions focused and under 50 lines
- Use meaningful variable names

Example:
```python
def parse_csv_file(file_path: str) -> pd.DataFrame:
    """
    Parse a CSV file and return a pandas DataFrame.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing the parsed data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.ParserError: If CSV is malformed
    """
    return pd.read_csv(file_path)
```

### TypeScript (Frontend)

- Follow the existing **ESLint configuration**
- Use **TypeScript strict mode** (no `any` types)
- Prefer **functional components** with hooks
- Use **descriptive prop names**
- Keep components under 200 lines (split if larger)

Example:
```typescript
interface DatasetCardProps {
  dataset: Dataset;
  onDelete: (id: string) => void;
}

export function DatasetCard({ dataset, onDelete }: DatasetCardProps) {
  // Component implementation
}
```

### Git Commits

Use conventional commit format:

- `Add: New feature or capability`
- `Fix: Bug fix`
- `Update: Modify existing feature`
- `Remove: Delete code or features`
- `Refactor: Code restructuring without behavior change`
- `Docs: Documentation changes`
- `Test: Add or update tests`

Example: `Add: Support for XLSX file upload with schema detection`

## Testing Guidelines

### Backend Tests

Create tests in `backend/<app>/tests.py`:

```python
from django.test import TestCase
from core.models import Dataset

class DatasetModelTest(TestCase):
    def test_dataset_creation(self):
        dataset = Dataset.objects.create(
            name="Test Dataset",
            slug="test-dataset"
        )
        self.assertEqual(dataset.name, "Test Dataset")
```

Run tests:
```bash
python manage.py test
```

### Frontend Testing

While formal tests aren't currently set up, ensure:
- No TypeScript errors: `npm run build`
- Manual testing of UI interactions
- Check browser console for errors

## Documentation

- Update relevant **README.md** files
- Add **inline code comments** for complex logic
- Update **API documentation** if endpoints change
- Include **usage examples** for new features

## Areas for Contribution

Looking for contribution ideas? Check these areas:

### High Priority
- [ ] Add comprehensive test coverage
- [ ] PostgreSQL support
- [ ] Async file processing
- [ ] Schema migration handling

### Medium Priority
- [ ] GraphQL API option
- [ ] Webhook notifications
- [ ] Batch operations
- [ ] Export datasets

### Documentation
- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] Deployment guides for specific platforms
- [ ] API usage examples

### DevOps
- [ ] GitHub Actions CI/CD
- [ ] Docker optimization
- [ ] Kubernetes manifests
- [ ] Monitoring setup

## Questions?

If you have questions about contributing:
- Open a **GitHub Discussion**
- Check existing **issues and PRs**
- Review the **architecture documentation** in `backend/ARCHITECTURE.md`

---

Thank you for contributing to File-to-API! 🚀
