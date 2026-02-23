import HeaderUser from "@/integrations/clerk/header-user";
import { SidebarInset } from "../ui/sidebar";

export function AppMain({ children }: { children: React.ReactNode }) {
    return (
        <SidebarInset className="h-svh overflow-hidden">
            <header className="flex justify-between h-16 bg-white z-10 shrink-0 items-center gap-2 border-b px-4">
                <span>Chat name here</span>
                <HeaderUser />
            </header>
            {children}
        </SidebarInset>
    );
}
