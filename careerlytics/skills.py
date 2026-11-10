
TAXONOMY = {
    # Programming
    "Python": ("Programming", ["python", "python3"]),
    "Java": ("Programming", ["java"]),
    "JavaScript": ("Programming", ["javascript", "es6"]),
    "TypeScript": ("Programming", ["typescript"]),
    "R": ("Programming", ["r programming", "rstudio", "r language"]),
    "C++": ("Programming", ["c++"]),
    "Scala": ("Programming", ["scala"]),
    # Databases
    "SQL": ("Database", ["sql", "t-sql", "pl/sql", "sql queries", "advanced sql"]),
    "MySQL": ("Database", ["mysql"]),
    "PostgreSQL": ("Database", ["postgresql", "postgres"]),
    "MongoDB": ("Database", ["mongodb", "mongo"]),
    "Redis": ("Database", ["redis"]),
    # Analytics & BI
    "Excel": ("Analytics & BI", ["excel", "ms excel", "microsoft excel", "advanced excel"]),
    "Power BI": ("Analytics & BI", ["power bi", "powerbi", "power-bi"]),
    "DAX": ("Analytics & BI", ["dax"]),
    "Power Query": ("Analytics & BI", ["power query"]),
    "Tableau": ("Analytics & BI", ["tableau"]),
    "VBA": ("Analytics & BI", ["vba", "excel vba", "macros"]),
    "Statistics": ("Analytics & BI", ["statistics", "statistical analysis", "hypothesis testing"]),
    "A/B Testing": ("Analytics & BI", ["a/b testing", "ab testing", "a/b tests"]),
    "Data Visualization": ("Analytics & BI", ["data visualization", "data visualisation", "data viz"]),
    "Data Modeling": ("Analytics & BI", ["data modeling", "data modelling", "dimensional modeling"]),
    # Python data stack
    "Pandas": ("Python Data Stack", ["pandas"]),
    "NumPy": ("Python Data Stack", ["numpy"]),
    "Matplotlib": ("Python Data Stack", ["matplotlib"]),
    "Seaborn": ("Python Data Stack", ["seaborn"]),
    "Scikit-learn": ("Python Data Stack", ["scikit-learn", "scikit learn", "sklearn"]),
    "Streamlit": ("Python Data Stack", ["streamlit"]),
    # ML / AI
    "Machine Learning": ("ML & AI", ["machine learning", "ml"]),
    "Deep Learning": ("ML & AI", ["deep learning"]),
    "NLP": ("ML & AI", ["nlp", "natural language processing"]),
    "TensorFlow": ("ML & AI", ["tensorflow"]),
    "PyTorch": ("ML & AI", ["pytorch"]),
    "Keras": ("ML & AI", ["keras"]),
    "XGBoost": ("ML & AI", ["xgboost"]),
    "Computer Vision": ("ML & AI", ["computer vision", "opencv"]),
    "Feature Engineering": ("ML & AI", ["feature engineering"]),
    "Time Series": ("ML & AI", ["time series", "time-series", "forecasting"]),
    "LLMs": ("ML & AI", ["llm", "llms", "large language models", "generative ai", "genai"]),
    "MLOps": ("ML & AI", ["mlops", "mlflow"]),
    # Data engineering
    "Spark": ("Data Engineering", ["spark", "pyspark", "apache spark"]),
    "Hadoop": ("Data Engineering", ["hadoop"]),
    "Kafka": ("Data Engineering", ["kafka", "apache kafka"]),
    "Airflow": ("Data Engineering", ["airflow", "apache airflow"]),
    "dbt": ("Data Engineering", ["dbt"]),
    "Snowflake": ("Data Engineering", ["snowflake"]),
    "BigQuery": ("Data Engineering", ["bigquery"]),
    "Databricks": ("Data Engineering", ["databricks"]),
    "ETL": ("Data Engineering", ["etl", "elt", "etl pipelines"]),
    "Data Warehousing": ("Data Engineering", ["data warehousing", "data warehouse", "data warehouses"]),
    # Cloud & DevOps
    "AWS": ("Cloud & DevOps", ["aws", "amazon web services"]),
    "Azure": ("Cloud & DevOps", ["azure", "microsoft azure"]),
    "GCP": ("Cloud & DevOps", ["gcp", "google cloud", "google cloud platform"]),
    "Docker": ("Cloud & DevOps", ["docker", "docker compose"]),
    "Kubernetes": ("Cloud & DevOps", ["kubernetes", "k8s"]),
    "Git": ("Cloud & DevOps", ["git", "github", "gitlab"]),
    "CI/CD": ("Cloud & DevOps", ["ci/cd", "cicd", "jenkins", "github actions"]),
    "Linux": ("Cloud & DevOps", ["linux", "unix"]),
    # Backend / web
    "REST APIs": ("Backend & Web", ["rest api", "rest apis", "restful", "restful apis"]),
    "Flask": ("Backend & Web", ["flask"]),
    "FastAPI": ("Backend & Web", ["fastapi"]),
    "Django": ("Backend & Web", ["django"]),
    "React": ("Backend & Web", ["react", "reactjs", "react.js"]),
    "Node.js": ("Backend & Web", ["node.js", "nodejs"]),
    "HTML/CSS": ("Backend & Web", ["html", "css", "html5", "css3"]),
    # Business & soft skills
    "Communication": ("Business", ["communication", "communication skills", "presentation skills"]),
    "Agile": ("Business", ["agile", "scrum"]),
    "Stakeholder Management": ("Business", ["stakeholder management", "stakeholder communication"]),
    "Requirements Gathering": ("Business", ["requirements gathering", "requirement gathering", "business requirements", "brd"]),
    "Jira": ("Business", ["jira"]),
}

SKILL_LIST = list(TAXONOMY)
SKILL_INDEX = {s: i for i, s in enumerate(SKILL_LIST)}
CATEGORY = {s: v[0] for s, v in TAXONOMY.items()}
ALIASES = {s: v[1] for s, v in TAXONOMY.items()}

# Skills that should be learned before another one (used to order the roadmap)
PREREQS = {
    "DAX": ["Power BI"], "Power Query": ["Excel"], "Pandas": ["Python"], "NumPy": ["Python"],
    "Scikit-learn": ["Python", "Pandas"], "Deep Learning": ["Machine Learning"],
    "TensorFlow": ["Python", "Deep Learning"], "PyTorch": ["Python", "Deep Learning"],
    "Keras": ["Deep Learning"], "XGBoost": ["Machine Learning"], "MLOps": ["Docker", "Machine Learning"],
    "LLMs": ["NLP"], "NLP": ["Machine Learning"], "Kubernetes": ["Docker"], "Airflow": ["Python"],
    "dbt": ["SQL"], "Snowflake": ["SQL"], "Spark": ["Python"], "Databricks": ["Spark"],
    "FastAPI": ["Python"], "Flask": ["Python"], "Django": ["Python"], "Streamlit": ["Python"],
    "React": ["JavaScript"], "Node.js": ["JavaScript"], "TypeScript": ["JavaScript"],
    "CI/CD": ["Git"], "Data Warehousing": ["SQL"], "ETL": ["SQL"], "Seaborn": ["Matplotlib"],
}

#Typical weeks to reach job-ready level per category (roadmap timeline estimate)
WEEKS = {
    "Programming": 8, "Database": 3, "Analytics & BI": 3, "Python Data Stack": 3, "ML & AI": 6,
    "Data Engineering": 5, "Cloud & DevOps": 4, "Backend & Web": 4, "Business": 2,
}
