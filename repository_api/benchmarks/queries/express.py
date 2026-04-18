"""
50 benchmark queries for expressjs/express.
Core files: lib/application.js, lib/express.js, lib/request.js, lib/response.js,
lib/router/index.js, lib/router/route.js, lib/router/layer.js, lib/view.js, lib/utils.js
"""
from benchmarks.queries import Query

REPO_NAME = "expressjs/express"

NL_QUERIES = [
    Query("ex_nl_01", "How does Express handle routing?", "natural_language", "Routing mechanism", ["lib/router/index.js", "lib/router/route.js"], ["route"]),
    Query("ex_nl_02", "How are middleware functions chained?", "natural_language", "Middleware chain", ["lib/router/index.js", "lib/router/layer.js"], ["handle"]),
    Query("ex_nl_03", "What is the request lifecycle in Express?", "natural_language", "Request flow", ["lib/router/index.js"], ["handle"]),
    Query("ex_nl_04", "How does Express send JSON responses?", "natural_language", "JSON response method", ["lib/response.js"], ["json"]),
    Query("ex_nl_05", "How are static files served?", "natural_language", "Static file serving", ["lib/express.js"], ["static"]),
    Query("ex_nl_06", "How does Express parse request parameters?", "natural_language", "Parameter parsing", ["lib/router/layer.js"], ["match"]),
    Query("ex_nl_07", "How does the view rendering engine work?", "natural_language", "Template rendering", ["lib/view.js", "lib/application.js"], ["render"]),
    Query("ex_nl_08", "How are cookies set in responses?", "natural_language", "Cookie handling", ["lib/response.js"], ["cookie"]),
    Query("ex_nl_09", "How does Express handle content negotiation?", "natural_language", "Content negotiation", ["lib/response.js", "lib/request.js"], ["accepts"]),
    Query("ex_nl_10", "How does the app.use() method work?", "natural_language", "Middleware mounting", ["lib/application.js"], ["use"]),
    Query("ex_nl_11", "How are error handling middleware defined?", "natural_language", "Error middleware", ["lib/router/index.js"], ["handle"]),
    Query("ex_nl_12", "How does Express handle redirects?", "natural_language", "Redirect responses", ["lib/response.js"], ["redirect"]),
    Query("ex_nl_13", "How does the request.ip property work?", "natural_language", "IP address resolution", ["lib/request.js"], ["ip"]),
    Query("ex_nl_14", "How are route parameters validated?", "natural_language", "Param validation", ["lib/router/index.js"], ["param"]),
    Query("ex_nl_15", "How does Express handle HTTP methods?", "natural_language", "HTTP method routing", ["lib/application.js", "lib/router/route.js"], ["get"]),
    Query("ex_nl_16", "How does res.send() determine content type?", "natural_language", "Content type detection", ["lib/response.js"], ["send"]),
    Query("ex_nl_17", "How does Express handle file downloads?", "natural_language", "File download", ["lib/response.js"], ["download"]),
    Query("ex_nl_18", "How are subdomains parsed from the host?", "natural_language", "Subdomain parsing", ["lib/request.js"], ["subdomains"]),
    Query("ex_nl_19", "How does Express set response headers?", "natural_language", "Header management", ["lib/response.js"], ["set"]),
    Query("ex_nl_20", "How does the app.listen() method create a server?", "natural_language", "Server creation", ["lib/application.js"], ["listen"]),
    Query("ex_nl_21", "How are query strings parsed?", "natural_language", "Query string parsing", ["lib/request.js"], ["query"]),
    Query("ex_nl_22", "How does Express create the application object?", "natural_language", "App factory", ["lib/express.js"], ["createApplication"]),
    Query("ex_nl_23", "How is the request body parsed?", "natural_language", "Body parsing", ["lib/express.js"], ["json"]),
    Query("ex_nl_24", "How are response status codes set?", "natural_language", "Status codes", ["lib/response.js"], ["status"]),
    Query("ex_nl_25", "What utility functions does Express use internally?", "natural_language", "Internal utilities", ["lib/utils.js"], ["flatten"]),
]

CODE_QUERIES = [
    Query("ex_code_01", "proto.route = function", "code", "Route method", ["lib/router/index.js"], ["route"]),
    Query("ex_code_02", "res.send = function", "code", "Send response", ["lib/response.js"], ["send"]),
    Query("ex_code_03", "res.json = function", "code", "JSON response", ["lib/response.js"], ["json"]),
    Query("ex_code_04", "res.redirect = function", "code", "Redirect method", ["lib/response.js"], ["redirect"]),
    Query("ex_code_05", "app.use = function", "code", "Middleware mount", ["lib/application.js"], ["use"]),
    Query("ex_code_06", "app.listen = function", "code", "Listen method", ["lib/application.js"], ["listen"]),
    Query("ex_code_07", "app.render = function", "code", "Render method", ["lib/application.js"], ["render"]),
    Query("ex_code_08", "function createApplication(", "code", "App factory", ["lib/express.js"], ["createApplication"]),
    Query("ex_code_09", "res.cookie = function", "code", "Cookie setter", ["lib/response.js"], ["cookie"]),
    Query("ex_code_10", "res.status = function", "code", "Status setter", ["lib/response.js"], ["status"]),
    Query("ex_code_11", "req.get = function", "code", "Header getter", ["lib/request.js"], ["get"]),
    Query("ex_code_12", "res.sendFile = function", "code", "Send file", ["lib/response.js"], ["sendFile"]),
    Query("ex_code_13", "res.download = function", "code", "Download method", ["lib/response.js"], ["download"]),
    Query("ex_code_14", "Layer.prototype.match", "code", "Layer matching", ["lib/router/layer.js"], ["match"]),
    Query("ex_code_15", "Layer.prototype.handle_request", "code", "Request handler", ["lib/router/layer.js"], ["handle_request"]),
    Query("ex_code_16", "Layer.prototype.handle_error", "code", "Error handler", ["lib/router/layer.js"], ["handle_error"]),
    Query("ex_code_17", "Route.prototype.dispatch", "code", "Route dispatch", ["lib/router/route.js"], ["dispatch"]),
    Query("ex_code_18", "app.param = function", "code", "Param handler", ["lib/router/index.js"], ["param"]),
    Query("ex_code_19", "module.exports = Route", "code", "Route export", ["lib/router/route.js"], ["Route"]),
    Query("ex_code_20", "res.set = function", "code", "Header setter", ["lib/response.js"], ["set"]),
    Query("ex_code_21", "View.prototype.render", "code", "View rendering", ["lib/view.js"], ["render"]),
    Query("ex_code_22", "res.type = function", "code", "Content type setter", ["lib/response.js"], ["type"]),
    Query("ex_code_23", "res.format = function", "code", "Format negotiation", ["lib/response.js"], ["format"]),
    Query("ex_code_24", "res.append = function", "code", "Header append", ["lib/response.js"], ["append"]),
    Query("ex_code_25", "app.engine = function", "code", "Template engine", ["lib/application.js"], ["engine"]),
]

ALL_QUERIES = NL_QUERIES + CODE_QUERIES
