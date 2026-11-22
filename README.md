# PRIVACHECK – AI-Powered GDPR Compliance Auditing Platform

## Overview

PRIVACHECK is an intelligent GDPR compliance auditing platform designed to analyze privacy policies, terms of service, and other legal documents.

The application leverages Artificial Intelligence, Natural Language Processing (NLP), and Retrieval-Augmented Generation (RAG) to identify potential GDPR compliance issues and generate structured audit reports with relevant recommendations.

## Key Features

- **User Authentication:** Secure registration, login, and account management.
- **AI-Powered Document Analysis:** Analyze privacy policies and legal documents.
- **GDPR Compliance Assessment:** Identify potential compliance gaps based on GDPR requirements.
- **RAG Integration:** Retrieve relevant regulatory knowledge to provide contextual answers.
- **AI Chatbot:** Interact with an intelligent assistant to ask GDPR-related questions.
- **Automated Audit Reports:** Generate structured reports containing findings and recommendations.
- **Audit History:** Track and review previous document analyses.
- **Admin Dashboard:** Manage users and monitor platform activities.

## Technologies Used

- **Programming Language:** Python
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Artificial Intelligence:** Large Language Models (LLMs)
- **NLP:** Natural Language Processing
- **Architecture:** Retrieval-Augmented Generation (RAG)
- **Database:** SQLite
- **Version Control:** Git & GitHub

## Project Architecture

The platform follows a modular architecture composed of:

- **Frontend Layer:** Provides the user interface and interaction with the platform.
- **Backend Layer:** Handles business logic, authentication, and audit processing.
- **AI Layer:** Processes legal documents and generates contextual responses.
- **Knowledge Base:** Stores regulatory information used by the RAG pipeline.
- **Database Layer:** Manages users, audit records, and application data.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ameni678/PRIVACHECK-RGPD-Audit.git
cd PRIVACHECK-RGPD-Audit
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file based on `.env.example` and configure the required API keys and application settings.

### 6. Run the application

Follow the backend and frontend startup instructions provided in the project configuration.

## Project Objectives

- Simplify GDPR compliance analysis.
- Automate the identification of potential regulatory issues.
- Integrate RAG techniques into legal document analysis.
- Provide explainable and contextual AI-generated recommendations.
- Explore the application of Generative AI to regulatory compliance.

## Future Improvements

- Extend the GDPR knowledge base.
- Improve compliance assessment accuracy.
- Add advanced document comparison.
- Introduce additional regulatory frameworks.
- Enhance audit report export and visualization.

## Author

**Amani Rattouli**

Academic Project – Artificial Intelligence & Data Science

---

**Disclaimer:** PRIVACHECK is an educational and decision-support tool. Its AI-generated assessments do not constitute legal advice or an official GDPR compliance certification.
