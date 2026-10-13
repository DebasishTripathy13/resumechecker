"""Static word lists used by the analysis services."""

ACTION_VERBS = frozenset({
    "accelerated", "achieved", "acquired", "adapted", "administered", "advised",
    "analyzed", "architected", "assembled", "assessed", "authored", "automated",
    "boosted", "built", "championed", "coached", "collaborated", "completed",
    "conceived", "conducted", "consolidated", "constructed", "consulted",
    "converted", "coordinated", "created", "cut", "debugged", "decreased",
    "defined", "delivered", "deployed", "designed", "developed", "devised",
    "diagnosed", "directed", "doubled", "drove", "eliminated", "enabled",
    "engineered", "enhanced", "established", "evaluated", "exceeded", "executed",
    "expanded", "expedited", "facilitated", "forecasted", "formulated", "founded",
    "generated", "grew", "guided", "headed", "identified", "implemented",
    "improved", "increased", "influenced", "initiated", "innovated", "inspected",
    "installed", "integrated", "introduced", "invented", "investigated", "launched",
    "led", "maintained", "managed", "maximized", "mentored", "migrated",
    "minimized", "modernized", "monitored", "negotiated", "optimized",
    "orchestrated", "organized", "overhauled", "oversaw", "partnered", "pioneered",
    "planned", "presented", "prioritized", "produced", "programmed", "proposed",
    "prototyped", "published", "raised", "rebuilt", "recruited", "redesigned",
    "reduced", "refactored", "reengineered", "resolved", "restructured",
    "revamped", "reviewed", "saved", "scaled", "secured", "shipped", "simplified",
    "solved", "spearheaded", "standardized", "streamlined", "strengthened",
    "supervised", "surpassed", "tested", "trained", "transformed", "tripled",
    "troubleshot", "unified", "upgraded", "validated", "won", "wrote",
})

WEAK_PHRASES = (
    "responsible for",
    "duties included",
    "duties include",
    "worked on",
    "helped with",
    "assisted with",
    "tasked with",
    "involved in",
    "participated in",
    "in charge of",
    "familiar with",
    "various tasks",
    "etc",
)

TECH_SKILLS = (
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "sql", "nosql", "html", "css",
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask",
    "fastapi", "spring", "spring boot", ".net", "graphql", "rest", "grpc",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
    "rabbitmq", "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "ansible", "jenkins", "github actions", "ci/cd", "linux", "git", "bash",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "spark",
    "hadoop", "airflow", "tableau", "power bi", "excel", "machine learning",
    "deep learning", "nlp", "computer vision", "data analysis", "data science",
    "microservices", "agile", "scrum", "jira", "figma", "selenium", "pytest",
    "junit", "oauth", "security", "networking", "llm", "generative ai",
)

SOFT_SKILLS = (
    "leadership", "communication", "teamwork", "collaboration",
    "problem solving", "problem-solving", "critical thinking", "mentoring",
    "stakeholder management", "time management", "adaptability", "negotiation",
    "presentation", "project management",
)

# Common English words plus job-posting boilerplate that should never count
# as a "keyword" when matching against a job description.
STOPWORDS = frozenset({
    "a", "about", "above", "across", "after", "all", "also", "an", "and", "any",
    "are", "as", "at", "be", "been", "being", "both", "but", "by", "can",
    "could", "do", "does", "each", "etc", "for", "from", "has", "have", "how",
    "if", "in", "into", "is", "it", "its", "may", "more", "most", "must", "not",
    "of", "on", "or", "other", "our", "out", "over", "per", "should", "so",
    "such", "than", "that", "the", "their", "them", "then", "there", "these",
    "they", "this", "those", "through", "to", "up", "us", "use", "using",
    "very", "via", "was", "we", "well", "were", "what", "when", "where",
    "which", "while", "who", "will", "with", "within", "would", "you", "your",
    # job-posting boilerplate
    "ability", "able", "apply", "candidate", "candidates", "company", "degree",
    "environment", "equivalent", "excellent", "experience", "experienced",
    "familiarity", "good", "great", "help", "ideal", "including", "job",
    "join", "knowledge", "looking", "new", "opportunity", "plus", "position",
    "preferred", "related", "required", "requirements", "responsibilities",
    "role", "seeking", "skills", "strong", "team", "understanding", "work",
    "working", "year", "years", "qualifications", "bonus", "benefits", "salary",
})
