**File:** `weather-microservice/README.md`

```markdown
# Weather Microservice

## Getting Started

Follow these steps in order before writing any code.

---

### Step 1: Install Dependencies

Make sure you are in the `weather-microservice` directory, then run:

```bash
pip install -r requirements.txt
```

---

### Step 2: Set Up Your Environment File

Check if a `.env` file already exists in the `weather-microservice` folder.
If it does not exist, create one by copying the given example file:

```bash
cp .env.example .env
```

---

### Step 3: Get AWS Credentials

Use my AWS credentials to log into learner lab: 

Once logged in:
1. Go to **Modules**
2. Click **Start Lab** to start a learner lab session — wait until the circle next to "AWS" turns green
3. Click **AWS Details**
4. Click **AWS CLI**
5. You will see three values — copy them one by one into your `.env` file:

```bash
AWS_ACCESS_KEY_ID=paste-value-here
AWS_SECRET_ACCESS_KEY=paste-value-here
AWS_SESSION_TOKEN=paste-value-here
```

> ENSURE TWO PEOPLE DONT GENERATE CREDENTIALS AT THE SAME TIME, WHEN YOU GENERATE CREDENTIALS. PASTE THEM INTO MESSENGER CHAT. SO ANOTHER PERSON CAN JUST COPY-PASTE INTO ENV FILE WIHTOUT NEEDING TO LOG-IN

> NOTE: These credentials expire when your lab session ends. Every time you start
> a new lab session you must repeat Step 3 and paste in the new values.


---

### Step 4: Verify Your Connection

Run the following to confirm you are connected to the correct AWS resources:

```bash
python src/dependencies/db_client.py
python src/dependencies/s3_client.py
```

You should see:
```
DynamoDB connected: clearpath-weather-data
S3 connected: clearpath-weather-data
```

If you see a connection error, check that:
- Your lab session is still active (green circle)
- You copied all three credential values correctly into `.env`
- There are no line breaks in the `AWS_SESSION_TOKEN` value

---
### Important Rules
- **Never commit your `.env` file** — it contains sensitive credentials
- **Never push the `venv/` folder** — teammates install dependencies themselves via `pip install -r requirements.txt`
```