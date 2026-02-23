import { createFileRoute } from "@tanstack/react-router";
import { ArrowLeft, Bot, Github, Plus, SearchCode } from "lucide-react";

export const Route = createFileRoute("/")({ component: App });

function App() {
    return (
        <div className="flex h-full w-full flex-col items-center justify-center bg-background p-8">
            <div className="relative mb-8 p-1 flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10">
                <Bot className="size-10 text-primary" />
                <Plus className="size-6 text-primary" />
                <Github className="size-10 w-10 text-primary" />
            </div>

            <div className="max-w-[420px] text-center">
                <h1 className="text-3xl font-bold tracking-tight text-foreground">
                    Code Repository Agent
                </h1>
                <p className="mt-4 text-muted-foreground">
                    Ready to explore your code? Select an indexed repository
                    from the sidebar to start a conversation with the AI agent.
                </p>
            </div>

            <div className="mt-10 grid w-full max-w-md grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="flex flex-col items-center rounded-xl border bg-card p-4 text-center shadow-sm">
                    <SearchCode className="mb-2 h-6 w-6 text-primary" />
                    <h3 className="text-sm font-semibold">Hybrid Search</h3>
                    <p className="text-xs text-muted-foreground">
                        Ask questions about logic, architecture and source code.
                    </p>
                </div>
                <div className="flex flex-col items-center rounded-xl border bg-card p-4 text-center shadow-sm">
                    <Github className="mb-2 h-6 w-6 text-primary" />
                    <h3 className="text-sm font-semibold">Live Indexing</h3>
                    <p className="text-xs text-muted-foreground">
                        Import any public GitHub repo.
                    </p>
                </div>
            </div>

            <div className="mt-12 flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
                <ArrowLeft className="h-4 w-4" />
                <span>Select a repo on the left to begin</span>
            </div>
        </div>
    );
}
