import { SidebarInset } from "../ui/sidebar";
import { AppPromptInput } from "./app-prompt-input";
import { Chat } from "./chat";

export function AppMain() {
    return (
        <SidebarInset>
            <header className="flex h-16 bg-white z-10 shrink-0 items-center gap-2 border-b px-4">
                Chat name here
            </header>
            <div className="flex flex-col">
                <Chat />
                <AppPromptInput />
            </div>
        </SidebarInset>
    );
}
