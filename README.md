## Every Time You Start Working
```bash
# 1. Navigate to your microservice and activate its venv
cd weather-microservice # or alert-microservice / transport-microservice
source venv/bin/activate

# 2. (Optional) Pull the latest changes from your develop branch (Good Practice)
git pull origin develop/X

# 3. Refresh your AWS credentials
# Log into the learner lab portal and update your .env file with new credentials
```

## Git & Branching Standards

To maintain a clean history and enable automated deployments, we follow a strict branching and commit convention.

### 1. Branch Naming Convention

All branches must follow the structure: `type/service-name/description`

| Type | Description | Example |
| --- | --- | --- |
| `feat/` | A new feature for a specific service | `feat/weather/s3-ingestion` |
| `fix/` | A bug fix | `fix/alert/api-timeout` |
| `refactor/` | Code changes that neither fix a bug nor add a feature | `refactor/transport/db-schema` |
| `chore/` | Updates to build scripts, tools, or libraries | `chore/common/update-precommit` |
| `docs/` | Documentation changes only | `docs/weather/api-endpoints` |

#### Service Names:

* `weather`
* `alert`
* `transport`
* `common` (For shared scripts or root-level changes)

---

### 2. The Development Workflow

We follow a **Feature Branch Workflow** to ensure code quality:

1. **Create a Branch:** Locally create a branch from `main`.
```bash
git checkout -b feat/weather/your-feature-name

```


2. **Small Commits:** Adhere to the **200-line limit**. If your change is larger, break it into multiple commits.
3. **ALICE-TODO-Local Validation:** Before pushing, `pre-commit` will automatically run formatting (`black`, `isort`) and linting (`flake8`).
4. **Open a Pull Request (PR):**
* Target the `main` branch.
* Ensure at least **one team member** reviews and approves the code.
* Evidence of comments/discussion must be visible in the PR before merging.

---

### 3. Commit Message Standards

Commit messages should be detailed and specific. Avoid generic messages like "fixed bug" or "updates."

**Good Example:**

```text
feat(weather): implement S3 event trigger for Lambda-Cleaner

- Added S3 bucket notification configuration
- Implemented O(1) metadata lookup logic

```

---

## Local Setup (One-Time)

To ensure your environment matches the team standards, run:
```bash
# Install pre-commit hooks (Ensure you are in the root/ClearPath directory)
cd ClearPath
pip install pre-commit
pre-commit install
sh util/setup.sh


# Set up your microservice environment (Only do it for the service you are working on)
cd weather-microservice
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements-dev.txt
deactivate
cd ..

# OR 

cd transport-microservice
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements-dev.txt
deactivate
cd ..

# OR 

cd alert-microservice
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements-dev.txt
deactivate
cd ..

```

After this, every `git commit` will automatically:
- Format your code with black
- Sort imports with isort
- Lint with flake8
- Reject commits over 200 lines
