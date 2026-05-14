# BI Methods — Generative AI (20251)

**Course repository** for *BI Methods — Generative AI* (semester 20251).
This folder contains lecture materials, notebooks, datasets, assignments, slides, and example code used in the course.

> Note: If you cloned this repository, see the **Setup** section below for environment instructions.

---

## Table of contents

* [Course overview](#course-overview)
* [Repository structure](#repository-structure)
* [Prerequisites](#prerequisites)
* [Setup (local / conda)](#setup-local--conda)
* [How to run notebooks](#how-to-run-notebooks)
* [Datasets and data usage](#datasets-and-data-usage)
* [Assignments and grading](#assignments-and-grading)
* [Examples & demos](#examples--demos)
* [Contributing](#contributing)
* [License](#license)
* [Contact / instructor info](#contact--instructor-info)

---

## Course overview

This repository supports a course on business intelligence (BI) methods with a focus on generative AI. The course covers foundational topics in generative models and practical workflows for applying them to BI tasks such as:

* Text generation and prompt engineering
* Retrieval-augmented generation (RAG)
* Vector embeddings and semantic search
* Building small production prototypes (demo apps)
* Responsible AI practices (bias, privacy, safety)
* Model selection and evaluation for BI tasks

Materials are provided as Jupyter notebooks, slides, example scripts, and datasets so students can reproduce the labs and complete assignments.

---

## Repository structure

> Note: the exact filenames in your `20251/` folder may vary. Replace the sample folders below with the actual names present in the directory.

```
20251/
├── notebooks/             # Jupyter notebooks for lectures and labs
├── slides/                # Lecture slides (PDF / PPTX)
├── assignments/           # Assignment prompts and submission templates
├── datasets/              # Small datasets used in labs (or links to larger datasets)
├── examples/              # Example scripts and demo apps
├── requirements.txt       # Python dependencies
├── environment.yml        # Conda environment (optional)
└── README.md              # This file
```

If your folder contains additional subfolders (e.g., `solutions/`, `resources/`, `images/`), include them following the same pattern.

---

## Prerequisites

Recommended software and accounts:

* Python 3.10+ (3.8+ may work but 3.10+ is recommended)
* Conda or Miniconda (recommended for reproducible environments)
* Git (for cloning)
* JupyterLab or Jupyter Notebook
* (Optional) Node.js and Yarn/npm if any demo web apps are included
* API keys if you plan to run cloud APIs (Azure OpenAI, OpenAI API, Hugging Face, etc.) — follow provider instructions and store keys in environment variables or a `.env` file (never commit keys).

---

## Setup (local / conda)

### Using conda (recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/msfasha/307307-BI-Methods-Generative-AI.git
   cd 307307-BI-Methods-Generative-AI/20251
   ```

2. Create the environment (if `environment.yml` present):

   ```bash
   conda env create -f environment.yml
   conda activate bi-generative-ai-20251
   ```

3. Or install from `requirements.txt`:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. Start JupyterLab:

   ```bash
   jupyter lab
   ```

### Environment variables & API keys

Create a `.env` file in the working directory (do **not** commit it) with contents like:

```
OPENAI_API_KEY=sk-...
AZURE_OPENAI_KEY=...
HF_API_TOKEN=...
```

Load these into your environment via `python-dotenv` or your shell before running notebooks.

---

## How to run notebooks

1. Open JupyterLab / Jupyter Notebook:

   ```bash
   jupyter lab
   ```
2. Navigate to `20251/notebooks/` and open the notebook you want to run.
3. Follow the instructions in the notebook. Many notebooks include a "Configuration" cell near the top where you must add API keys or paths.

Tips:

* If a notebook relies on large models or cloud APIs, consider using smaller local models or mock responses for development.
* Restart the kernel and run all cells if you see inconsistent state.

---

## Datasets and data usage

* Small example datasets are stored in `datasets/`. If the course requires larger datasets, those may be linked (not stored in the repo) and instructions for download will be provided in the relevant notebook or assignment.
* Always verify dataset licenses and privacy constraints before using or sharing derived data.
* Do not commit private or sensitive data (PII, proprietary data) to the repository.

---

## Assignments and grading

* Assignment prompts are in `assignments/`. Each assignment directory contains:

  * `README.md` with task description and deliverables
  * A starter notebook or script
  * A submission template (e.g., `.ipynb` or `.py`)
* Follow academic integrity rules — all work must be your own unless group work is explicitly allowed.
* Submission method (GitHub classroom, LMS upload, or email) and deadlines will be provided by the instructor.

---

## Examples & demos

* `examples/` contains runnable demos and small projects demonstrating:

  * Prompt engineering patterns
  * RAG pipeline (indexing + query)
  * Embedding generation and nearest neighbor search
  * Small web demo for interacting with a model (if included)

Read the README inside each example subfolder for run instructions (some demos require additional setup such as a local vector DB or Docker).

---

## Responsible AI & safety

This course emphasizes responsible development of generative AI systems. Key points covered in materials:

* Understand model limitations and hallucinations
* Privacy considerations with prompts and datasets
* Mitigation strategies for harmful or biased outputs
* Prompting & evaluation practices to improve safety and reliability

---

## Troubleshooting

If you encounter issues:

1. Revisit the top cells in notebooks to ensure paths and API keys are configured.
2. Confirm you installed the correct Python version and dependencies.
3. Check the notebook kernel for errors and restart kernel if needed.
4. Consult the course staff or raise an issue in the repository (if enabled).

---

## Contributing

Contributions are welcome (code fixes, improved examples, typos). If you plan to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Add tests/examples and update documentation.
4. Open a pull request describing your changes.

Follow the repository's code style and include clear commit messages. If the repository is used for course grading, coordinate with the instructor before submitting major changes.

---

## License

Unless otherwise specified in the repository, check the `LICENSE` file at the repository root. Typical licenses for course material include MIT or CC-BY; confirm the exact license included in the repo before reuse.

---

## Contact / Instructor

If you need help with course material, please contact the course instructor or TA as listed by the course (or the repository owner). If you prefer, open an issue in the repository for non-sensitive requests.

