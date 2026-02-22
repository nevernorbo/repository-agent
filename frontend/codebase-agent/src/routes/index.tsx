import { AppMain } from "@/components/main/app-main";
import { AppSidebar } from "@/components/sidebar/app-sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({ component: App });

function App() {
    return (
        <SidebarProvider>
            <AppSidebar />
            <AppMain />
        </SidebarProvider>
    );
}
