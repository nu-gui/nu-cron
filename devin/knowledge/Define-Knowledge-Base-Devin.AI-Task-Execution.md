📌 Defining Devin’s Knowledge Base for AI Task Execution

📌 Purpose:
The Knowledge Base serves as Devin AI’s memory for storing critical project information, guidelines, and execution rules. By pre-loading key knowledge into Devin, we ensure:
	•	AI recalls best practices & project-specific details automatically.
	•	Reduced redundant queries & misinterpretations.
	•	Optimized AI execution without excessive ACU usage.
	•	Consistent high-quality AI-generated code & outputs.

📍 1. Defining Structured Knowledge Categories

To ensure Devin AI retrieves relevant information at the right time, we will categorize knowledge into structured sections.

Category	Purpose	Example Topics
Coding Standards & Best Practices	Ensure AI-generated code follows industry standards	PEP 8 (Python), TypeScript Linting, Rust Safety Rules
AI Workflows & Automation Rules	Define structured AI execution workflows	Task breakdowns, ACU limits, rollback strategies
Project-Specific Guidelines	Store project structure, API design, database schema	Next.js frontend structure, Hono API guidelines
Security & Compliance	Enforce security protocols for AI-generated code	OAuth2 authentication, encryption, AI security restrictions
AI Testing & Validation	Establish test execution & validation criteria	AI test requirements, error handling, test automation rules

📍 2. Example Knowledge Base Entries

📝 Entry 1: Coding Standards & Best Practices

Trigger Description: "Coding Guidelines"
Content:

# 🔍 Coding Guidelines  
Devin AI must follow these standards when generating code:  
- **Python** → Follow **PEP 8** coding standards. Functions must include **docstrings**.  
- **TypeScript** → Adhere to **Airbnb’s TypeScript Style Guide**. Use strict typing.  
- **Rust** → Follow Rustfmt styling rules, ensure **memory safety & proper error handling**.  
- **Component Naming** → Use **PascalCase for components**, **camelCase for functions & variables**.  
- **Security Practices** → Never hardcode **API keys, secrets, or credentials**. Use `.env` files for sensitive data.  
- **Testing Requirements** → AI-generated code must **include unit tests before submission**.  

✅ Why? → Ensures AI-generated code maintains high-quality, readability, and security compliance.

📝 Entry 2: AI Workflows & Automation Rules

Trigger Description: "AI Workflow Execution Rules"
Content:

# ⚙️ AI Workflow Execution Rules  
- **Devin AI must execute tasks in small, incremental steps (≤ 1 ACU per request).**  
- **Development Workflow:**  
  1️⃣ **AI generates code** → 2️⃣ **AI executes tests** → 3️⃣ **AI documents code** → 4️⃣ **Human developer reviews & approves**.  
- **Rollback Strategy:**  
  - If AI-generated code fails validation, **Devin should rollback to the last stable version**.  
  - **Developers can rewind AI memory & retry task execution** if necessary.  
- **Pull Request (PR) Requirements:**  
  - AI-generated PRs must include a **human-readable summary of changes**.  
  - PRs must be **approved by a developer before merging into `main`**.  

✅ Why? → Defines how Devin AI should structure its task execution to optimize ACU usage.

📝 Entry 3: Project-Specific Guidelines

Trigger Description: "Project Architecture & API Rules"
Content:

# 📦 Project Architecture & API Guidelines  
- **Frontend Framework** → Next.js (TypeScript) must follow **modular component-based design**.  
- **Backend APIs** → All backend services must use **Hono (TypeScript) for edge computing** & **FastAPI (Python) for AI model execution**.  
- **Database & ORM** → Store structured data in **Neon PostgreSQL**, with **Prisma ORM** handling schema management.  
- **Authentication** → Implement **Clerk for OAuth2 & JWT authentication flows**.  
- **AI Processing Layer** → All AI model requests must be **routed through AISuite for cost-optimized inference selection**.  

✅ Why? → Ensures Devin AI follows the correct software architecture when generating new features.

📝 Entry 4: Security & Compliance

Trigger Description: "Security Best Practices"
Content:

# 🛡️ Security Best Practices  
- **Encryption:**  
  - All **sensitive data must be encrypted at rest & in transit**.  
- **Authentication & Authorization:**  
  - Use **OAuth2 & JWT authentication** for secure access control.  
- **AI Security Rules:**  
  - Devin **must never generate code that exposes plaintext passwords**.  
  - All user inputs must be **sanitized to prevent SQL Injection & XSS attacks**.  
- **Logging & Auditing:**  
  - All system logs must be stored in **Helicone & ELK Stack** for monitoring AI-generated code behavior.  

✅ Why? → Prevents AI-generated code from introducing security vulnerabilities.

📝 Entry 5: AI Testing & Validation

Trigger Description: "AI Test Automation Rules"
Content:

# 🧪 AI Test Automation Rules  
- **Unit Testing**  
  - Devin must write **unit tests using Jest (TypeScript) & pytest (Python) before PR submission**.  
- **Integration Testing**  
  - AI must **validate API endpoints and microservices integration before deployment**.  
- **Error Handling**  
  - AI should **log errors instead of silently failing**.  
- **Acceptance Criteria**  
  - AI-generated features must be validated against **TASKS.md requirements** before merging.  

✅ Why? → Ensures Devin AI applies structured testing before finalizing code changes.

📍 3. Adding Entries to Devin AI’s Knowledge Section

To add these entries:
1️⃣ Navigate to Devin AI > Settings > Knowledge
2️⃣ Click “Add Knowledge”
3️⃣ Enter the Trigger Description and Content
4️⃣ Click Save

