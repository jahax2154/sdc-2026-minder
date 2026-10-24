# Minder — SDC Hackathon 2026

An AI-assisted career exploration and personalised reskilling platform that helps students, fresh graduates and early-career professionals understand their existing skills, explore career opportunities and get well-prepared dor future workforce changes.

## Team Information
| Field | Details |
|-------|---------|
| Team Name | AINewBee |
| Team Domain | Domain 1 - The Aiversity Future-Ready Workforce Domain |
| SDG Track (1-17) | SDG 4 - Quality Education |
| Team Leader | Lee Yi Cheng |
| University | Asia Pacific University, University Technology Malaysia |
| Number of Members | 3 |

## Links
| Resource | Link |
|-------|---------|
| GitHub Repository | https://github.com/jahax2154/sdc-2026-minder |
| Live Demo | https://aiversecity-career-compass.replit.app |
| RunPod Endpoint |  |
| Slide Deck | slide link |
| Demo Video | Youtube link |

## Overview

### Problem

Rapid developments in artificial intelligence are changing the skills required across many industries. However, students, fresh graduates, and early-career professionals may struggle to identify which of their existing skills remain relevant, what career opportunities match their abilities, and which new skills they should develop.

Many career guidance resources provide general recommendations without clearly explaining skill gaps or helping users understand how different AI adoption scenarios could influence their future career pathways.

### Solution

**Aiversecity Career Compass** is an AI-assisted career exploration and personalised reskilling platform designed to help users make informed decisions about their professional development.

Users can upload a CV/resume or manually enter their skills and proficiency levels. The platform analyses their confirmed skills, recommends suitable career pathways, and identifies skills they may need to develop.

It also incorporates updatable AI-related trend signals, explainable career matching, hypothetical AI-disruption scenarios, and personalised learning recommendations. These features help users explore career possibilities and prepare for changing workforce requirements.

The platform also connects relevant careers and skills to the United Nations Sustainable Development Goals (SDGs), particularly **SDG 4 — Quality Education**, to promote lifelong learning and career readiness.

### Key Features

- **CV/Resume Skill Extraction** — Upload a PDF or DOCX resume to identify existing skills, with options to review and correct extracted information.
- **Personalised Skills Profile** — Record skills, proficiency levels, learning preferences, and career interests.
- **Explainable Career Matching** — Receive ranked career recommendations based on skill coverage, with clear explanations of matching skills and gaps.
- **Future Skill-Gap Analysis** — Identify important skills to develop based on career requirements and documented scenario assumptions.
- **AI and Workforce Trend Signals** — Explore updatable external information with visible sources, publication dates, and limitations.
- **Personalised Learning Pathway** — Follow an ordered reskilling roadmap with estimated learning time and relevant educational resources.
- **AI-Disruption Scenarios** — Compare career recommendations under Moderate and Fast AI Disruption assumptions.
- **SDG Integration** — Understand how career development and relevant skills connect to the United Nations Sustainable Development Goals.
- **AI Career Assistant** — Provides an interface for career-related questions through the project's AI service integration. Demo responses are identified separately from live model inference.

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| **Backend** | Node.js, Express, TypeScript |
| **API Specification & Validation** | OpenAPI, Zod |
| **CV Processing** | PDF.js, Mammoth |
| **Career Recommendation** | Explainable weighted skill-coverage scoring, skill-gap analysis, and ML-assisted recommendations |
| **Trend Data** | Public RSS feeds with source and date information |
| **AI Integration** | Integrated ML service and AI career assistant |
| **Machine Learning / GPU** | RunPod — ML model deployment and inference |
| **Development & Hosting** | Replit |
| **Database** | SQLite |


## Project Structure

The project follows a monorepo architecture that separates the frontend, backend, machine-learning components, and shared API contracts.

**Repository Status:** The frontend and backend source code are currently maintained in a separate development branch. The project structure below will be verified and updated once the branch is merged into `main`.

```text
sdc-2026-minder/
│
├── .github/
│   └── workflows/          # GitHub workflows
│
├── apps/
│   ├── web/                # Frontend application (pending merge) **
│   └── api/                # Backend application (pending merge) **
│
├── contracts/              # Shared API contracts
│
├── ml/
│   ├── configs/            # Machine learning configurations
│   ├── experiments/        # Model experiments
│   ├── src/
│   │   └── minder_ml/      # Machine learning source directory
│   └── tests/              # Machine learning tests
│
├── scripts/                # Project scripts
├── tests/                  # Project-level tests
├── .gitignore
└── README.md
```


### Architecture

Aiversecity Career Compass follows a modular full-stack architecture that connects the user interface, application logic, and machine-learning service.

```text
                  USER
                    |
                    v
       +---------------------------+
       | React + TypeScript        |
       | Frontend (Replit)         |
       |                           |
       | - CV Upload               |
       | - Skills Profile          |
       | - Career Dashboard        |
       | - Learning Pathway        |
       | - AI Career Chatbot       |
       +---------------------------+
                    |
                    v
       +---------------------------+
       | Express + TypeScript      |
       | Backend API (Replit)      |
       |                           |
       | - AI Service Adapter      |
       | - API Validation          |
       | - Trend Feed Integration  |
       +---------------------------+
              |             |
              v             v
     +----------------+  +-------------------+
     | RunPod ML      |  | Public RSS        |
     | Service        |  | Trend Sources     |
     |                |  |                   |
     | - ML Inference |  | - Trend Signals   |
     | - AI Analysis  |  | - Source Metadata |
     +----------------+  +-------------------+
              |             |
              +------+------+
                     |
                     v
       +---------------------------+
       | Career Compass Results    |
       |                           |
       | - Career Recommendations  |
       | - Future Skill Gaps       |
       | - AI Scenario Comparison  |
       | - Reskilling Pathways     |
       +---------------------------+
                     |
                     v
                USER DASHBOARD
```

### How the System Works

1. **User Profile:** Users upload a PDF/DOCX resume or manually enter their skills. Extracted skills are reviewed and confirmed before analysis.

2. **Frontend Processing:** The React application manages the user interface, profile information, career exploration and learning pathway presentation.

3. **Backend Communication:** The Express backend handles AI service requests, validates data and retrieves available trend signals.

4. **Machine Learning Integration:** The backend communicates with the RunPod-hosted ML service to obtain AI-assisted analysis and recommendations.

5. **Career and Skill Analysis:** The application combines explainable skill matching, skill-gap calculations, AI-assisted recommendations and scenario-based assessments.

6. **Learning Recommendations:** Users receive personalised reskilling pathways with learning resources, estimated durations and relevant Sustainable Development Goal connections.

7. **Result Presentation:** The dashboard presents recommendations and supporting explanations to help users make informed career-development decisions.



