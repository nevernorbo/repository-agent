import { AppPromptInput } from "@/components/main/app-prompt-input";
import { Chat } from "@/components/main/chat";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/repository/$id")({
    component: Repository,
});

function Repository() {
    const { id } = Route.useParams();

    console.log("Id: ", id);

    // use effect to fetch load the repo into memory -> wait for fetching to complete, after that the user can enter a prompt
    return (
        <div className="flex flex-1 flex-col overflow-hidden">
            <Chat />
            <AppPromptInput />
        </div>
    );
}
