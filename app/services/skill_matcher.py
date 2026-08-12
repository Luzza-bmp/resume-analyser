import re

SKILLS_DB = {

    # Programming Languages
    "python", "java", "c", "c++", "c#", "go", "golang",
    "rust", "swift", "kotlin", "scala", "r", "matlab",
    "perl", "php", "ruby", "dart", "typescript",
    "javascript", "objective-c", "bash", "shell scripting",

    # Web Development
    "html", "html5", "css", "css3", "bootstrap",
    "tailwind css", "jquery", "ajax", "react", "reactjs",
    "nextjs", "vue", "vuejs", "angular", "angularjs",
    "nodejs", "express", "expressjs", "flask", "django",
    "fastapi", "spring", "spring boot", "asp.net",
    "rest api", "graphql", "soap", "json", "xml",

    # Mobile Development
    "flutter", "react native", "android", "android studio",
    "ios", "xcode", "kotlin", "swift",

    # Databases
    "sql", "mysql", "postgresql", "sqlite", "oracle",
    "mongodb", "redis", "firebase", "mariadb",
    "nosql", "cassandra", "neo4j", "dynamodb",

    # Cloud
    "aws", "amazon web services", "azure",
    "google cloud", "gcp", "cloud computing",
    "heroku", "vercel", "netlify",

    # DevOps
    "git", "github", "gitlab", "bitbucket",
    "docker", "kubernetes", "jenkins",
    "terraform", "ansible", "ci/cd",
    "linux", "ubuntu", "unix",

    # AI / Machine Learning
    "machine learning", "deep learning",
    "artificial intelligence", "ai",
    "nlp", "natural language processing",
    "computer vision", "opencv",
    "tensorflow", "keras", "pytorch",
    "scikit-learn", "xgboost",
    "lightgbm", "huggingface",
    "transformers", "langchain",
    "llm", "generative ai",
    "prompt engineering",

    # Data Science
    "data science", "data mining",
    "data analysis", "data visualization",
    "statistics", "pandas", "numpy",
    "matplotlib", "seaborn",
    "plotly", "scipy", "jupyter",
    "excel", "power bi", "tableau",
    "etl", "data warehouse",

    # Cybersecurity
    "cybersecurity", "penetration testing",
    "ethical hacking", "network security",
    "cryptography", "wireshark",
    "metasploit", "nmap",
    "owasp", "firewall",

   
    # Operating Systems
    "windows", "linux", "macos",

    # Software Engineering
    "oop", "object oriented programming",
    "design patterns",
    "software architecture",
    "microservices",
    "multithreading",
    "concurrency",

   

    # Version Control
    "git", "github",
    "gitlab",

    # UI/UX
    "figma",
    "adobe xd",
    "photoshop",
    "illustrator",
    "canva",
    "ui design",
    "ux design",
    "wireframing",
    "prototyping",
    "seo",
   # Design
    "graphic design",
    "video editing",
    "photography",
    "adobe premiere pro",
    "after effects",
    "blender",
    "autocad",
    "solidworks",

    # Soft Skills
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "critical thinking",
    "analytical thinking",
    "decision making",
    "time management",
    "adaptability",
    "creativity",
    "presentation",
    "negotiation",
    "collaboration",
    "customer service",
    "public speaking",
    "mentoring",
    "conflict resolution",
    "attention to detail",
    "organizational skills",
    "multitasking",

    # Research
    "research",
    "technical writing",
    "documentation",

    # Languages
    "english",
    "hindi",
    "nepali",
    "french",
    "german",
    "spanish",
    "chinese",
    "japanese",

    # Miscellaneous
    "api",
    "oauth",
    "jwt",
    "socket programming",
    "web scraping",
    "beautifulsoup",
    "selenium",
    "streamlit",
    "opencv",
    "pymupdf",
    "regex",
    "rapidfuzz",
    "computer networks",
    "operating systems",
    "database management system",
    "dbms",
    "compiler design",
    "data structures",
    "algorithms",
    "object oriented design",
    "software development",
    "full stack development",
    "backend development",
    "frontend development"
   

# Data Engineering
"data engineering", "etl",  "apache beam",
"azure synapse",
"data pipeline", "data modeling",

# Embedded Systems & IoT
"arduino", "raspberry pi", "embedded c",
"microcontrollers", "esp32", "esp8266",
"iot", "mqtt", "embedded systems",



# Blockchain
"blockchain", "ethereum", "solidity",
"smart contracts", "web3", "hyperledger",
"cryptocurrency",

# Game Development
"unity", "unreal engine", "godot",
"game development", "opengl",
"directx", "shader programming",

# CAD / Engineering
"autocad", "solidworks", "catia",
"ansys", "fusion 360", "revit",
"civil 3d",







# Human Resources
"recruitment", "talent acquisition",
"employee engagement", "onboarding",
"performance management",
"hr analytics",

# Sales
"sales", "lead generation",
"crm", "salesforce",
"business development",
"cold calling",
"customer relationship management",

# Customer Support
"customer support", "technical support",
"help desk", "ticketing",
"zendesk", "freshdesk",
"wordpress",

# Graphic Design
"adobe photoshop",
"adobe illustrator",
"davinci resolve",
"adobe premiere pro",
"after effects",
"motion graphics",

# Cloud & Infrastructure
"vmware",
"virtualization",
"openstack",
"load balancing",
"nginx",
"apache server",

# Mathematics
"linear algebra",
"calculus",
"probability",
"optimization",
"numerical methods",


# Office Administration
"data entry",
"record keeping",
"event management",

# Education
"teaching",
"lesson planning",
"curriculum development",
"classroom management",
"online tutoring",
# Networking
"ccnp",
"network troubleshooting",
"lan",
"wan",
"wireless networking",
"cisco packet tracer",
}


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS_DB:
        if re.search(rf"\b{re.escape(skill)}\b", text): #regex word boundary to match whole words only
            found_skills.append(skill)

    return sorted(list(set(found_skills)))
