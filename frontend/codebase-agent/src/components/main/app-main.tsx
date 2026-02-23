import HeaderUser from "@/integrations/clerk/header-user";
import { SidebarInset } from "../ui/sidebar";
import { AppPromptInput } from "./app-prompt-input";
import { Chat } from "./chat";

export function AppMain() {
    return (
        <SidebarInset className="h-svh overflow-hidden">
            <header className="flex justify-between h-16 bg-white z-10 shrink-0 items-center gap-2 border-b px-4">
                <span>Chat name here</span>
                <HeaderUser />
            </header>
            <div className="flex flex-1 flex-col overflow-hidden">
                <Chat />
                <AppPromptInput />
            </div>
        </SidebarInset>
    );
}
