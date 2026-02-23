import { SidebarInset } from "../ui/sidebar";

export function AppMain({ children }: { children: React.ReactNode }) {
    return (
        <SidebarInset className="h-svh overflow-hidden">
            {children}
        </SidebarInset>
    );
}
