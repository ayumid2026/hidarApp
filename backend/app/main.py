# Development
# app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Production (replace with your actual domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-username.github.io",
        "https://hidar.app"  # Your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
