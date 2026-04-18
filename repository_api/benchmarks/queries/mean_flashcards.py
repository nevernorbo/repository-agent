"""
50 benchmark queries for nevernorbo/mean-flashcards.
MEAN-stack flashcard app: Angular 19 frontend, Express backend, MongoDB.
"""
from benchmarks.queries import Query

REPO_NAME = "nevernorbo/mean-flashcards"

NL_QUERIES = [
    Query("mf_nl_01", "How are flashcards created and stored in the database?", "natural_language", "Flashcard creation logic", ["backend/models/flashcard.js", "backend/routes/flashcards.js"], ["FlashcardSchema"]),
    Query("mf_nl_02", "What authentication mechanism is used for user login?", "natural_language", "Auth middleware and login", ["backend/routes/auth.js", "backend/middleware/auth.js"], ["login"]),
    Query("mf_nl_03", "How does the API handle error responses?", "natural_language", "Error handling", ["backend/app.js"], ["errorHandler"]),
    Query("mf_nl_04", "How are flashcard collections shared between users?", "natural_language", "Sharing logic", ["backend/routes/collections.js"], ["share"]),
    Query("mf_nl_05", "What is the database schema for a flashcard?", "natural_language", "Mongoose schema", ["backend/models/flashcard.js"], ["FlashcardSchema"]),
    Query("mf_nl_06", "How does the Angular frontend communicate with the backend API?", "natural_language", "HTTP service", ["frontend/nice-cards/src/app/services"], ["ApiService"]),
    Query("mf_nl_07", "How is user registration implemented?", "natural_language", "Signup route", ["backend/routes/auth.js"], ["register"]),
    Query("mf_nl_08", "What routing structure does the Express backend use?", "natural_language", "Router setup", ["backend/app.js"], ["router"]),
    Query("mf_nl_09", "How are environment variables loaded and managed?", "natural_language", "Config management", ["backend/app.js"], ["dotenv"]),
    Query("mf_nl_10", "What is the component structure of the Angular frontend?", "natural_language", "Angular components", ["frontend/nice-cards/src/app/app.component.ts"], ["AppComponent"]),
    Query("mf_nl_11", "How does the app handle JWT token validation?", "natural_language", "JWT verification", ["backend/middleware/auth.js"], ["verify"]),
    Query("mf_nl_12", "How are flashcard collections organized?", "natural_language", "Collection model", ["backend/models/collection.js"], ["CollectionSchema"]),
    Query("mf_nl_13", "What is the MongoDB connection setup?", "natural_language", "Mongoose connection", ["backend/app.js"], ["connect"]),
    Query("mf_nl_14", "How does the frontend handle form validation?", "natural_language", "Angular forms", ["frontend/nice-cards/src/app/components"], ["FormGroup"]),
    Query("mf_nl_15", "What middleware does the Express server use?", "natural_language", "Middleware chain", ["backend/app.js"], ["cors"]),
    Query("mf_nl_16", "How is the Docker setup configured for development?", "natural_language", "Docker config", ["docker-compose.yaml"], []),
    Query("mf_nl_17", "What Angular routing configuration is used?", "natural_language", "Angular routes", ["frontend/nice-cards/src/app/app.routes.ts"], ["routes"]),
    Query("mf_nl_18", "How does the application delete a flashcard?", "natural_language", "Delete endpoint", ["backend/routes/flashcards.js"], ["delete"]),
    Query("mf_nl_19", "What password hashing strategy is used?", "natural_language", "Password hashing", ["backend/routes/auth.js"], ["bcrypt"]),
    Query("mf_nl_20", "How does the frontend display a list of flashcards?", "natural_language", "List component", ["frontend/nice-cards/src/app/components"], ["FlashcardListComponent"]),
    Query("mf_nl_21", "How are user profiles stored?", "natural_language", "User model", ["backend/models/user.js"], ["UserSchema"]),
    Query("mf_nl_22", "What is the main entry point of the backend server?", "natural_language", "Server startup", ["backend/app.js"], ["listen"]),
    Query("mf_nl_23", "How are HTTP interceptors used in the Angular app?", "natural_language", "Auth interceptor", ["frontend/nice-cards/src/app/interceptors"], ["intercept"]),
    Query("mf_nl_24", "How does the app handle updating a flashcard?", "natural_language", "Update endpoint", ["backend/routes/flashcards.js"], ["update"]),
    Query("mf_nl_25", "What navigation structure does the frontend use?", "natural_language", "Navbar component", ["frontend/nice-cards/src/app/components"], ["NavbarComponent"]),
]

CODE_QUERIES = [
    Query("mf_code_01", "router.post('/flashcards'", "code", "POST route for flashcards", ["backend/routes/flashcards.js"], ["post"]),
    Query("mf_code_02", "mongoose.Schema({", "code", "Schema definition", ["backend/models/flashcard.js"], ["Schema"]),
    Query("mf_code_03", "module.exports = router", "code", "Router export", ["backend/routes/flashcards.js"], ["router"]),
    Query("mf_code_04", "jwt.sign(", "code", "JWT token generation", ["backend/routes/auth.js"], ["sign"]),
    Query("mf_code_05", "jwt.verify(", "code", "JWT verification", ["backend/middleware/auth.js"], ["verify"]),
    Query("mf_code_06", "@Component({", "code", "Angular component decorator", ["frontend/nice-cards/src/app/app.component.ts"], ["Component"]),
    Query("mf_code_07", "@Injectable({", "code", "Angular service decorator", ["frontend/nice-cards/src/app/services"], ["Injectable"]),
    Query("mf_code_08", "this.http.get(", "code", "Angular HTTP GET", ["frontend/nice-cards/src/app/services"], ["get"]),
    Query("mf_code_09", "this.http.post(", "code", "Angular HTTP POST", ["frontend/nice-cards/src/app/services"], ["post"]),
    Query("mf_code_10", "bcrypt.compare(", "code", "Password comparison", ["backend/routes/auth.js"], ["compare"]),
    Query("mf_code_11", "mongoose.connect(", "code", "MongoDB connection", ["backend/app.js"], ["connect"]),
    Query("mf_code_12", "app.use(cors(", "code", "CORS middleware", ["backend/app.js"], ["cors"]),
    Query("mf_code_13", "export class AppComponent", "code", "Main Angular component", ["frontend/nice-cards/src/app/app.component.ts"], ["AppComponent"]),
    Query("mf_code_14", "Router()", "code", "Express Router init", ["backend/routes/flashcards.js"], ["Router"]),
    Query("mf_code_15", "res.status(401).json(", "code", "Unauthorized response", ["backend/middleware/auth.js"], ["status"]),
    Query("mf_code_16", "findById(", "code", "Mongoose findById", ["backend/routes/flashcards.js"], ["findById"]),
    Query("mf_code_17", "findByIdAndUpdate(", "code", "Mongoose update", ["backend/routes/flashcards.js"], ["findByIdAndUpdate"]),
    Query("mf_code_18", "findByIdAndDelete(", "code", "Mongoose delete", ["backend/routes/flashcards.js"], ["findByIdAndDelete"]),
    Query("mf_code_19", "new FormGroup({", "code", "Angular reactive form", ["frontend/nice-cards/src/app/components"], ["FormGroup"]),
    Query("mf_code_20", "subscribe(", "code", "RxJS subscription", ["frontend/nice-cards/src/app/components"], ["subscribe"]),
    Query("mf_code_21", "express.json()", "code", "JSON parser middleware", ["backend/app.js"], ["json"]),
    Query("mf_code_22", "ngOnInit()", "code", "Angular lifecycle hook", ["frontend/nice-cards/src/app/components"], ["ngOnInit"]),
    Query("mf_code_23", "canActivate(", "code", "Angular route guard", ["frontend/nice-cards/src/app/guards"], ["canActivate"]),
    Query("mf_code_24", "bcrypt.hash(", "code", "Password hashing", ["backend/routes/auth.js"], ["hash"]),
    Query("mf_code_25", "app.listen(", "code", "Server listen", ["backend/app.js"], ["listen"]),
]

ALL_QUERIES = NL_QUERIES + CODE_QUERIES
