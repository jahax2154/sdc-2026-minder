# Minder — SDC Hackathon 2026

Minder is an AI-assisted career exploration and personalised reskilling platform that helps students, fresh graduates, and early-career professionals identify their strengths, explore career opportunities, and prepare for future workforce changes.

## Team Information
| Field | Details |
|-------|---------|
| Team Name | AINewBee |
| Team Domain | Domain 1 - The Aiversecity Future-Ready Workforce Domain |
| SDG Track (1-17) | SDG 4 - Quality Education |
| Team Leader | Lee Yi Cheng |
| University | Asia Pacific University of Technology & Innovation (APU); Universiti Teknologi Malaysia (UTM) |
| Number of Members | 3 |

## Links
| Resource | Link |
|-------|---------|
| GitHub Repository | https://github.com/jahax2154/sdc-2026-minder |
| Live Demo | https://aesthetic-baklava-2da854.netlify.app |
| RunPod Endpoint | https://console.runpod.io/serverless/user/endpoint/0387furb08gke2 |
| Slide Deck | https://canva.link/67te6g9azdjgt61 |
| Demo Video | https://youtu.be/l9xjHBjcycM |

## Overview

### Problem

Rapid developments in artificial intelligence are changing the skills required across many industries. However, students, fresh graduates, and early-career professionals may struggle to identify which of their existing skills remain relevant, what career opportunities match their abilities, and which new skills they should develop.

Many career guidance resources provide general recommendations without clearly explaining skill gaps or helping users understand how different AI adoption scenarios could influence their future career pathways.

### Solution

**Minder** is an AI-assisted career exploration and personalised reskilling platform designed to help users make informed decisions about their professional development.

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
│   ├── web/                # Frontend application (pending merge) 
│   └── api/                # Backend application (pending merge) 
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

Minder follows a modular full-stack architecture that connects the user interface, application logic, and machine-learning service.

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
       | Minder Results    |
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


## How to Run

Minder is developed and deployed using Replit. The application consists of a React frontend, an Express backend, and an integrated machine-learning service hosted on RunPod.

### Option 1 — Run on Replit (Recommended)

The easiest way to access the application is through our deployed prototype:

**Live Application:** https://aesthetic-baklava-2da854.netlify.app

To run the application in the Replit development environment:

1. Open the Minder project in Replit.
2. Ensure the required environment variables are configured securely using Replit Secrets.
3. Start the project's existing development workflow using the **Run** button.
4. Open the **Preview** panel to access the application.
5. Test the CV upload, career recommendations, skill-gap analysis, learning pathways, and AI career assistant.


### Option 2 — Run Locally

The application uses a Node.js and TypeScript workspace managed with pnpm.

**Prerequisites:**
- Node.js
- pnpm
- Git

After the frontend and backend development branch has been merged into `main`, the local setup can be completed using the following workflow.

```bash
# 1. Clone the GitHub repository
git clone https://github.com/jahax2154/sdc-2026-minder

# 2. Enter the project folder
cd sdc-2026-minder

# 3. Install dependencies
pnpm install

# 4. Run the application
# Confirm the correct workspace command after the branch merge
```

**Pending verification:** The final application startup commands, required Node.js and pnpm versions, and environment-variable names will be confirmed after the development branch is merged.

Do not commit API keys, model credentials, or private configuration files to GitHub.

### Run Tests

The Replit application includes frontend tests, API integration checks, and TypeScript validation.

The following commands apply to the previously exported Replit workspace and must be verified against the final merged GitHub repository:

```bash
# Frontend tests
pnpm --filter @workspace/career-compass run test

# AI integration tests
pnpm --filter @workspace/api-server run test:ai

# TypeScript checks
pnpm run typecheck

# Frontend production build
pnpm --filter @workspace/career-compass run build
```


## How We Use Replit

Replit serves as the primary development and hosting platform for the Minder web application. Our team used Replit to develop, test, refine, and deploy the frontend and backend components.

### Development

- **Frontend Development:** Developed the web application using React, TypeScript, Vite, Tailwind CSS, and shadcn/ui.
- **Backend Development:** Implemented an Express and TypeScript backend to support API communication, external trend-data retrieval, and AI service integration.
- **UI/UX Design:** Designed and refined the *Calm Horizon* interface, focusing on minimalist layouts, accessible navigation, and a comfortable learning experience.
- **AI Integration:** Implemented an AI service adapter to communicate with the team's machine-learning service hosted through RunPod.
- **AI-Assisted Development:** Used Replit Agent to assist with code generation, interface refinement, integration, and testing. Generated changes were reviewed and tested during development.

### Testing

Replit was used to run and verify the application during development, including:

- Frontend component and functionality tests.
- TypeScript type checking.
- Production build verification.
- API and AI integration tests.
- Responsive interface checks across desktop, tablet, and mobile layouts.
- Manual testing of CV uploads, career recommendations, skill-gap analysis, and learning pathways.

### Hosting and Deployment

Minder is deployed using Replit.

**Live Prototype:** https://aesthetic-baklava-2da854.netlify.app

The deployed application provides access to the career exploration platform, including the CV analysis interface, personalised career recommendations, learning pathways, AI scenarios, SDG connections, and the AI career assistant.

### Credentials and Security

Sensitive credentials, including external AI service authentication details, are configured through secure environment settings rather than being hardcoded into frontend source code.

The application is designed to separate backend communication from client-side interactions when accessing external AI services.

### Proof of Replit Usage

Evidence of Replit usage is included in the submission documentation.

**Proof of Use:** [Replit Proof of Use](submission/SDC2026_AINewBee_Replit_POU.pdf)


## How We Use RunPod

RunPod is used as the cloud computing platform for the machine-learning component of Minder. It supports AI-powered career guidance and skill analysis through a model service integrated with our Replit application.

### Machine Learning Workload

The machine-learning component supports the platform's AI-assisted features, including:

- **Skill Analysis:** Analysing user skill profiles to support personalised career guidance.
- **Future Skill Recommendations:** Generating suggestions about skills users may develop for their selected career pathways.
- **AI Career Assistant:** Supporting career-related questions and explanations through the chatbot interface.

The AI-generated recommendations complement the application's explainable skill-matching algorithm and scenario-based assessments.

### RunPod Setup

The team's machine-learning service is hosted using RunPod.

- **Deployment Type:** [Specify GPU Pod or Serverless Endpoint]
- **Model Name and Version:** [Enter the actual model used]
- **GPU Type:** [Enter GPU model if using a GPU Pod]
- **Model Framework:** [Enter actual framework, e.g. PyTorch or Transformers]
- **Endpoint:** [Enter the deployed inference endpoint or state how the service is accessed]

### Integration with Replit

The application follows this communication flow:

```text
User
  |
  v
Replit Frontend (React)
  |
  v
Replit Backend (Express)
  |
  v
RunPod ML Service
  |
  v
AI-generated analysis
  |
  v
Minder Dashboard
```

The frontend communicates with the Express backend, which sends structured requests to the RunPod-hosted model service and processes the returned responses.

The platform also retains its existing explainable career-matching and learning-pathway functionality independently of the external AI service.

### Example API Request

The following is a conceptual example of an analysis request. The actual request format must follow the deployed model's API contract.

```json
{
  "profile": {
    "skills": [
      {
        "skillId": "python",
        "level": 3
      },
      {
        "skillId": "sql",
        "level": 2
      }
    ]
  },
  "selectedCareerId": "data-analyst",
  "scenario": "fast"
}
```

The model service returns structured analysis that the application can use to present AI-assisted recommendations and explanations.

### Responsible AI and Data Handling

- Uploaded CVs are processed to identify relevant skills.
- Users can review and correct extracted skills before analysis.
- AI-generated recommendations are intended to support career decision-making, not guarantee future employment.
- Model limitations and hypothetical scenario assumptions should be communicated clearly.
- API credentials must be stored securely and excluded from the public repository.

### Proof of RunPod Usage

Evidence of RunPod usage is included in the submission documentation.

**Proof of Use:** [RunPod Proof of Use](submission/SDC2026_AINewBee_Runpod_POU.pdf)


## Challenges & Learnings

During the development of Minder, our team encountered several challenges involving system integration, user experience design, data reliability, and project coordination.

### 1. Integrating Frontend, Backend, and Machine Learning

One of our main challenges was integrating the React frontend and Express backend with the machine-learning service developed separately by another team member.

To address this, we adopted a modular architecture with defined API contracts, allowing the web application and ML components to be developed and tested independently.

**What we learned:** Clear API specifications and communication between team members are essential when integrating independently developed software components.

### 2. Designing an Accessible and User-Friendly Interface

Our initial interface contained several information-heavy sections, making the platform potentially overwhelming for users who were unfamiliar with career analytics.

We refined the design into **Calm Horizon**, a minimalist interface using sage-green accents, simplified navigation, spacious layouts, and clearer learning pathways.

**What we learned:** Effective UI/UX design is not simply about visual appearance. Presenting information progressively can make complex features easier to understand and encourage users to continue learning.

### 3. Providing Explainable Career Recommendations

Career recommendation systems can become difficult for users to trust when they cannot understand how recommendations are generated.

We addressed this by using transparent skill-coverage scoring, displaying relevant skill gaps, and explaining the assumptions behind future AI-disruption scenarios.

**What we learned:** Explainability and transparency are important when building AI-assisted systems that support personal decisions.

### 4. Managing External Trend Data

Our platform incorporates external trend signals, which introduce challenges involving data availability, accuracy, and interpretation.

We implemented source attribution, publication dates, refresh functionality, and appropriate error-handling mechanisms.

**What we learned:** External information should be presented with its sources and limitations. Published attention or news coverage should not be misrepresented as actual hiring demand.

### 5. Coordinating Development and Version Control

Our team developed different system components across Replit, GitHub branches, and the ML development environment.

Maintaining compatible interfaces and coordinating code changes required careful communication and task allocation.

**What we learned:** Version control, modular development, and clearly assigned responsibilities help teams collaborate more effectively under time constraints.

## Future Improvements

Although Minder provides a functional prototype, several improvements could enhance its capabilities and user experience in future versions.

- [ ] **Expanded Career Database** — Support a wider range of industries, occupations, and career pathways.
- [ ] **Improved Labour-Market Intelligence** — Integrate additional reliable job-market datasets to strengthen future skill recommendations.
- [ ] **Enhanced AI Recommendations** — Improve model evaluation and recommendation quality using appropriate datasets and testing methods.
- [ ] **Multilingual Support** — Provide additional language options to improve accessibility for Malaysian users.
- [ ] **Employer and Education Partnerships** — Explore collaboration with employers and training providers to improve the relevance of career and learning recommendations.


## Team

Our team consists of three members working collaboratively on the design, development, documentation, and integration of Minder.

| Name | Role | GitHub |
|---|---|---|
| Lee Yi Cheng | **Full-Stack Developer** — Replit frontend and backend development, UI/UX design, API integration, and deployment | [@yicheng-0612](https://github.com/yicheng-0612) |
| Phuah Jun Hong | **Machine Learning Engineer** — ML model development, training, evaluation, and RunPod integration | [@jahax2154](https://github.com/jahax2154) |
| Lau Wen Le | **Documentation & Project Coordinator** — Technical documentation, project proposal, presentation materials, submission preparation, and team coordination | [@WenLe0317](https://github.com/WenLe0317) |

## Submission Checklist

- [X] Team name, Domain 1, and SDG 4 track are correctly stated.
- [X] GitHub repository is publicly accessible to judges.
- [ ] Live Replit application link is working.
- [X] Presentation slide deck link has been added.
- [ ] Demo video link has been added.
- [X] Replit proof of use is included in `submission/`.
- [X] RunPod proof of use is included in `submission/`.
- [X] Preliminary submission document is completed (`SDC2026_AINewBee_Preliminary.pdf`).
- [X] Technical & Tools Declaration is completed (`SDC2026_AINewBee_TechDeclaration.pdf`).
- [X] All submission documents use the registered team name.
- [X] Frontend, backend, and ML source code are available in the final repository.
- [X] Installation and testing instructions have been verified.
- [X] No API keys, passwords, or other secrets are committed to GitHub.
- [X] Apache License 2.0 is included in the repository.

## License

This project is licensed under the [Apache License 2.0](LICENSE).




