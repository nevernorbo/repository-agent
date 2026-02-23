import { Chat } from "@/components/main/chat";
import { useAuth } from "@clerk/clerk-react";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/repository/$id")({
    component: Repository,
});

function Repository() {
    const { id } = Route.useParams();

    const repoId = id;
    const repository = decodeURIComponent(id);
    const { userId, isLoaded } = useAuth();
    const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

    useEffect(() => {
        // Guard clause: ensure we have all required IDs before patching
        if (!isLoaded || !userId || !repoId) return;

        const newSessionId = crypto.randomUUID();
        setActiveSessionId(newSessionId);

        const syncAgentContext = async () => {
            try {
                const response = await fetch(
                    `http://localhost:8100/apps/agent/users/${userId}/sessions/${newSessionId}`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            state: {
                                repository: repository,
                            },
                        }),
                    }
                );

                if (!response.ok) {
                    console.error(
                        "Failed to create agent state:",
                        response.statusText
                    );
                } else {
                    console.log("Session created!");
                }
            } catch (error) {
                console.error("Error syncing agent state:", error);
            }
        };

        syncAgentContext();
    }, [repoId, userId, isLoaded]);

    if (!userId || !activeSessionId) return null;

    return (
        <div className="flex flex-1 flex-col overflow-hidden">
            <header className="flex justify-between h-16 bg-white z-10 shrink-0 items-center gap-2 border-b px-4">
                <span>{repository}</span>
            </header>
            <Chat
                repository={repository}
                userId={userId}
                sessionId={activeSessionId}
            />
        </div>
    );
}
