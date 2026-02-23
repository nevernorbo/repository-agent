import { Chat } from "@/components/main/chat";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/repository/$id")({
    component: Repository,
});

function Repository() {
    const { id } = Route.useParams();
    const repository = decodeURIComponent(id);

    // Set the state in the Agent API

    return (
        <div className="flex flex-1 flex-col overflow-hidden">
            <header className="flex justify-between h-16 bg-white z-10 shrink-0 items-center gap-2 border-b px-4">
                <span>{repository}</span>
            </header>
            <Chat repository={repository} />
        </div>
    );
}
